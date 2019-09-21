"""
A game about a beetle.
"""
import logging
import math
import pdb  # pylint: disable=unused-import
import random
import time
from typing import Dict, List, Tuple

import pyxel

LOGGER = logging.getLogger("Beetle Charm logger")
HANDLER = logging.StreamHandler()
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)
LOGGER.info("Beetle Charm initialized.")

Coords = Tuple[int, int]
Rect = Tuple[int, int, int, int]
Asset = Dict[str, List[Rect]]


def invert_left(x_pos: int, y_pos: int, width: int, height: int) -> Rect:
    """Invert a grid horizontally."""
    return (x_pos, y_pos, -1 * width, height)


def invert_down(x_pos: int, y_pos: int, width: int, height: int) -> Rect:
    """Invert a grid vertically."""
    return (x_pos, y_pos, width, -1 * height)


def four_directions(north: Rect, east: Rect) -> Tuple[Rect, Rect, Rect, Rect]:
    """We can generate all directions if N and E are supplied."""
    south = invert_down(*north)
    west = invert_left(*east)
    return (north, east, south, west)


def advance(direction: int, speed: int) -> Tuple[float, float]:
    """Return delta_x and delta_y for the velocity given.
    With 0 being north, 2 east, 4 south, etc.
    """
    direction %= 8
    (delta_x, delta_y) = (
        (0, -1),  # north
        (1, -1),  # northeast
        (1, 0),  # east
        (1, 1),  # southeast
        (0, 1),  # south
        (-1, 1),  # southwest
        (-1, 0),  # west
        (-1, -1),  # northwest
    )[direction]
    LOGGER.info(
        "Advancing in direction %s: delta_x = %s; delta_y=%s",
        direction,
        delta_x,
        delta_y,
    )
    return (delta_x * speed, delta_y * speed)


class Sprite:
    """A graphics manager for a game object."""

    def __init__(
        self, x: int, y: int, asset: Asset, transparent_color: int = 0
    ):
        self.position = [x, y]
        self.asset = asset["main"][0]
        self.trans = transparent_color

    @property
    def width(self):
        """The image's width."""
        return abs(self.asset[2])

    @property
    def height(self):
        """The image's height."""
        return abs(self.asset[3])

    def in_bounds(self, pos: Coords, bounds: Rect) -> bool:
        """Would the sprite be in bounds at a given position?"""
        ok_left = pos[0] >= bounds[0]
        ok_right = pos[0] + self.width <= bounds[0] + bounds[2]
        ok_up = pos[1] >= bounds[1]
        ok_down = pos[1] + self.height <= bounds[1] + bounds[3]
        return all((ok_left, ok_right, ok_up, ok_down))

    def draw(self):
        """Draw the sprite to the screen."""
        pyxel.blt(*self.position, 0, *self.asset, self.trans)


class VisibleMap:
    """
    The map on which the game is played.
    """

    def __init__(self, bounds):
        LOGGER.info("Making the map.")
        plate_assets = (
            (16, 0, 8, 8),
            (24, 0, 8, 8),
            (16, 8, 8, 8),
            (24, 8, 8, 8),
        )
        padded_map_size = math.ceil(bounds[2] / 8)
        screen_positions = [
            [i * 8, j * 8]
            for j in range(padded_map_size)
            for i in range(math.ceil(bounds[2] / 8))
        ]
        self.bounds = bounds
        self.plates = []
        for i, pos in enumerate(screen_positions):
            tile = random.choice(plate_assets)
            if random.random() > 0.5:
                tile = invert_down(*tile)
            if random.random() > 0.5:
                tile = invert_left(*tile)
            if i % 2 == 0:
                tile = invert_down(*tile)
            sprite = Sprite(*pos, asset={"main": (tile,)})
            self.plates.append(sprite)

    def update(self):
        """Inter-turn logic."""
        # to do: check whether a new tile needs to be rendered.

    def draw(self):
        """Blit the image of the plates to the screen."""
        for plate in self.plates:
            plate.draw()


class Player:
    """
    The person playing the game.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, bounds):
        LOGGER.info("Making the player.")
        self.bounds = bounds
        self.position = [
            random.randrange(bounds[0], bounds[2]),
            random.randrange(bounds[1], bounds[3]),
        ]
        self.asset_key = "main"  # to toggle for walk animation
        self.assets = {
            "main": four_directions((0, 0, 8, 8), (0, 8, 8, 8)),  # (N, E)
            "alt": four_directions((8, 0, 8, 8), (8, 8, 8, 8)),
        }
        self.pointing = random.choice([0, 2, 4, 6])  # A cardinal direction.
        LOGGER.info(
            "Beetle initialized at %s, %s pointing at %s.",
            *self.position,
            self.pointing,
        )
        self.sprite = Sprite(
            *self.position, asset=self.assets, transparent_color=0
        )
        self.rhythm = 0
        self.speed = 0

    def rotate(self, direction):
        """Turn the object around."""
        assert direction in (
            -1,
            0,
            1,
        )  # counterclockwise, straight, clockwise
        self.pointing %= 8
        LOGGER.info("Turning %s to %s", direction, self.pointing)

    def update(self):
        """Inter-turn logic."""

        # Update sprite with properties
        self.sprite.position = self.position
        self.update_asset()

    def update_asset(self):
        """Inter-turn logic.

        Update the sprite to use the correct asset for the direction the sprite
        is pointing and its walk cycle.
        """
        LOGGER.debug("Asset coords: %s", self.sprite.asset)
        # Convert from the eight directions to the four sprite assets.
        index = int(self.pointing / 2)
        LOGGER.debug("INDEX %s", index)
        self.sprite.asset = self.assets[self.asset_key][index]

    def walk(self, direction, distance=5):
        """Move the sprite a certain distance."""
        self.pointing = direction
        if distance:
            movement = advance(self.pointing, distance)
            self.asset_key = "alt" if self.asset_key == "main" else "main"
            hypothetical_pos = [
                self.position[0] + movement[0],
                self.position[1] + movement[1],
            ]
            if self.sprite.in_bounds(hypothetical_pos, self.bounds):
                self.position = hypothetical_pos
                LOGGER.debug(
                    "Walking in %s direction to %s, %s",
                    movement,
                    *self.position,
                )
            else:
                LOGGER.info("Bumped into a wall.")

    def draw(self):
        """Draw the player's sprite."""
        self.sprite.draw()


class App:
    """
    Main game code.
    """

    def __init__(self):
        """Initial game setup."""
        LOGGER.info("Making the app.")
        self.start = time.clock()
        bounds = (0, 0, 55, 55)
        pyxel.init(*bounds[2:], caption="Beetle Charm")
        pyxel.load("assets/beetle-box.pyxel")
        self.player = Player(bounds)
        self.visible_map = VisibleMap(bounds)
        self.things = [self.visible_map, self.player]
        pyxel.playm(0, loop=True)

    def run(self):
        """Start the game using the pyxel engine."""
        pyxel.run(self.update, self.draw)

    def update(self):
        """Update the game settings."""
        # This could use a refactor, but it's pointless to refactor before we
        # know what all the controls should be.

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        elif pyxel.btnp(pyxel.KEY_W):
            self.player.walk(0)
        elif pyxel.btnp(pyxel.KEY_D):
            self.player.walk(2)
        elif pyxel.btnp(pyxel.KEY_S):
            self.player.walk(4)
        elif pyxel.btnp(pyxel.KEY_A):
            self.player.walk(6)

        for objekt in self.things:
            objekt.update()

    def draw(self):
        """Draw everything."""
        pyxel.cls(1)
        for objekt in self.things:
            objekt.draw()


def main():
    """Main control flow function."""
    app = App()
    LOGGER.info("Beetle Charm loaded successfully.")
    app.run()
    LOGGER.info("Thank you for playing.")


if __name__ == "__main__":
    main()
