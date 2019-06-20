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
LOGGER.setLevel(logging.DEBUG)
LOGGER.info('Beetle Charm initialized.')

Coords = Tuple[int, int]
Rect = Tuple[int, int, int, int]
Asset = Dict[str, List[Rect]]


def invert_left(x_pos: int, y_pos: int, width: int, height: int) -> Rect:
    """Invert a grid horizontally."""
    return (x_pos, y_pos, -1 * width, height)


def invert_down(x_pos: int, y_pos: int, width: int, height: int) -> Rect:
    """Invert a grid vertically."""
    return (x_pos, y_pos, width, -1 * height)


def four_directions(north: Rect, east: Rect) -> Tuple[Rect, Rect,
                                                      Rect, Rect]:
    """We can generate all directions if N and E are supplied."""
    south = invert_down(*north)
    west = invert_left(*east)
    return (north, east, south, west)


def build_asset_lib(asset: Asset) -> Asset:
    """
    With an asset containing a N and an E view, create rotations to return the
    following views, in order:
    :param n: the asset's north-facing view.
    :param ne: the asset's northeast-facing view.
    :param e: the asset's east-facing view.
    """
    primary = asset['main']
    alt = asset.get('alt') or ()
    assert len(primary) >= 2  # todo
    asset['main'] = four_directions(*primary)
    if alt:
        asset['alt'] = four_directions(*alt)
    return asset


def advance(direction: int, speed: int) -> Tuple[float, float]:
    """Return delta_x and delta_y for the velocity given.
    With 0 being north, 2 east, 4 south, etc.,
    """
    direction %= 8
    (delta_x, delta_y) = (
        (0, -1),   # north
        (1, -1),   # northeast
        (1, 0),    # east
        (1, 1),    # southeast
        (0, 1),    # south
        (-1, 1),   # southwest
        (-1, 0),   # west
        (-1, -1),  # northwest
    )[direction]
    LOGGER.info("Advancing in direction {}: delta_x = {}; delta_y={}".format(
        direction, delta_x, delta_y
    ))
    return (delta_x * speed, delta_y * speed)


class Sprite:
    """Anything simple enough to be drawn just by blitting it to the screen."""
    def __init__(self, x: int, y: int, asset_lib: Asset,
                 transparent_color: int = 0):
        self.x_pos = x
        self.y_pos = y
        self.asset_key = 'main'  # To toggle for walk animation
        self.asset_lib = build_asset_lib(asset_lib)
        self.asset = asset_lib['main'][0]
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
        pyxel.blt(self.x_pos, self.y_pos, 0, *self.asset, self.trans)


class VisibleMap:
    """
    The map on which the game is played.
    """
    def __init__(self, bounds):
        plate_assets = ((16, 0, 8, 8),
                        (24, 0, 8, 8),
                        (16, 8, 8, 8),
                        (24, 8, 8, 8))
        padded_map_size = math.ceil(bounds[2]/8)
        screen_positions = [[i * 8, j * 8] for j in range(padded_map_size)
                            for i in range(math.ceil(bounds[2]/8))]
        self.bounds = bounds
        self.plates = []
        for i, pos in enumerate(screen_positions):
            tile = random.choice(plate_assets)
            if random.random() > .5:
                tile = invert_down(*tile)
            if random.random() > .5:
                tile = invert_left(*tile)
            if i % 2 == 0:
                tile = invert_down(*tile)
            sprite = Sprite(*pos, asset_lib={'main': (tile,)})
            self.plates.append(sprite)

    def update(self):
        """Inter-turn logic."""
        # todo: check whether a new tile needs to be rendered.

    def draw(self):
        """Blit the image of the plates to the screen."""
        for plate in self.plates:
            plate.draw()


class Player:
    """
    The person playing the game.
    """
    def __init__(self, bounds):
        self.bounds = bounds
        self.x_pos = random.randrange(bounds[0], bounds[2])
        self.y_pos = random.randrange(bounds[1], bounds[3])
        self.tempo = 0
        self.assets = {
            'main': [
                (0, 0, 8, 8),  # N
                (0, 8, 8, 8),  # E
            ],
            'alt': [
                (8, 0, 8, 8),  # N
                (8, 8, 8, 8),  # E
            ],
        }
        self.pointing = random.choice([0, 2, 4, 6])  # A cardinal direction.
        LOGGER.info("Beetle initialized at {}, {} pointing at {}.".format(
            self.x_pos, self.y_pos, self.pointing))
        self.sprite = Sprite(self.x_pos, self.y_pos, asset_lib=self.assets,
                             transparent_color=0)
        self.game_location = []
        self.rhythm = 0
        self.speed = 0
        self.points = 0
        self.alive = True

    def rotate(self, direction):
        """Turn the object around."""
        assert direction in (-1, 0, 1)  # counterclockwise, straight, clockwise
        self.prev_pointing = self.pointing
        self.pointing += direction
        self.pointing %= 8
        LOGGER.info(f"Turning {direction} to {self.pointing}")

    def update(self):
        """Inter-turn logic."""
        # Speed limit.
        if self.speed < -1:
            self.speed = -1
        elif self.speed > 2:
            self.speed = 2

        # Update sprite with properties
        self.rhythm += 1
        self.rhythm %= 4
        if self.rhythm == 2:
            self.walk()
        self.sprite.x_pos = self.x_pos
        self.sprite.y_pos = self.y_pos
        self.update_asset()

    def update_asset(self):
        """Inter-turn logic.

        Update the sprite to use the correct asset for the direction the sprite
        is pointing and its walk cycle.
        """
        if self.pointing % 2 == 0:
            index = int(self.pointing/2)
        else:
            index = int(self.prev_pointing/2)
        self.sprite.asset = self.sprite.asset_lib[self.sprite.asset_key][index]

    def walk(self):
        """Move the sprite according to its walking speed."""
        if self.speed:
            movement = advance(self.pointing, self.speed)
            self.sprite.asset_key = 'alt' if self.sprite.asset_key == 'main' else 'main'  # noqa
            hypothetical_pos = (self.x_pos + movement[0],
                                self.y_pos + movement[1])
            if self.sprite.in_bounds(hypothetical_pos, self.bounds):
                self.x_pos, self.y_pos = hypothetical_pos
                LOGGER.debug("Walking in %s direction to %s, %s", movement,
                             self.x_pos, self.y_pos)
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
        self.start = time.clock()
        bounds = (0, 0, 55, 55)
        pyxel.init(*bounds[2:], caption="Beetle Charm")
        pyxel.load('assets/beetle-box.pyxel')
        self.player = Player(bounds)
        self.visible_map = VisibleMap(bounds)
        self.things = [self.visible_map, self.player]
        pyxel.playm(0, loop=True)

    def run(self):
        """Start the game using the pyxel engine."""
        pyxel.run(self.update, self.draw)

    def update(self):
        """Update the game settings."""
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        elif pyxel.btnp(pyxel.KEY_W):
            self.player.speed += 1
        elif pyxel.btnp(pyxel.KEY_S):
            self.player.speed -= 1
        elif pyxel.btnp(pyxel.KEY_A):
            self.player.rotate(-1)
        elif pyxel.btnp(pyxel.KEY_D):
            self.player.rotate(1)

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


if __name__ == '__main__':
    main()
