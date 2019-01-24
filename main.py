import logging
import pyxel
import random
import itertools

import pdb

logger = logging.getLogger("Beetle-Charm-logger")
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
# 'Beetle Charm logger.', level=logging.INFO)
logger.info('Beetle Charm initialized.')


def invert_left(x, y, width, height):
    return (x, y, -1 * width, height)


def invert_down(x, y, width, height):
    return (x, y, width, -1 * height)


start = (16, 0, 8, 8)
assert invert_left(*start) == (16, 0, -8, 8)
assert invert_down(*start) == (16, 0, 8, -8)


def eight_directions(n, ne, e):
    '''
    Return the following views of an asset, in order.
    :param n: the asset's north-facing view.
    :param ne: the asset's northeast-facing view.
    :param e: the asset's east-facing view.
    '''
    se = invert_down(*ne)
    s = invert_down(*n)
    sw = invert_left(*se)
    w = invert_left(*e)
    nw = invert_left(*ne)
    return (n, ne, e, se, s, sw, w, nw)


def advance(direction: int, backwards=False):
    '''
    With 0 being north, 2 east, 4 south, etc.,
    :return: (dx, dy) for the direction given.
    '''
    if backwards is True:
        direction += 4
    direction %= 8
    (dx, dy) = ((0, -1),   # north
                (1, -1),   # northeast
                (1, 0),    # east
                (1, 1),    # southeast
                (0, 1),    # south
                (-1, 1),   # southwest
                (-1, 0),   # west
                (-1, -1),  # northwest
                )[direction]
    logger.info("Advancing {}in direction {}: dx= {}; dy={}".format(
                        'backwards ' if backwards else '', direction,
                        dx, dy))
    return (dx, dy)


class Sprite:
    '''
    Anything simple enough to be drawn just by blitting it to the screen.
    '''
    def __init__(self, x, y, asset_coords_n, asset_coords_ne=None,
                 asset_coords_e=None, transparent_color=0):
        self.x = x
        self.y = y
        self.asset = asset_coords_n
        if asset_coords_ne and asset_coords_e:
            self.asset_rotation = eight_directions(asset_coords_n,
                                                   asset_coords_ne,
                                                   asset_coords_e)
        self.asset = asset_coords_n[:]
        self.trans = transparent_color

    def point_asset(self, direction):
        '''
        Return the correct asset coordinates for the direction the sprite is
        pointing.
        '''
        assert 0 <= direction <= 7  # with 0 being north, 2 east, 4 south, etc.
        self.asset = self.asset_rotation[direction]

    def draw(self):
        pyxel.blt(self.x, self.y, 0, *self.asset, self.trans)


class VisibleMap:
    '''
    The map on which the game is played.
    '''
    def __init__(self):
        plate_assets = [
                         (16, 0, 8, 8),
                         (24, 0, 8, 8),
                         (16, 8, 8, 8),
                         (24, 8, 8, 8),
                        ]
        screen_positions = [[i * 8, j * 8] for j in range(15)
                            for i in range(20)]
        self.plates = []
        for i, pos in enumerate(screen_positions):
            tile = random.choice(plate_assets)
            if random.random() > .5:
                tile = invert_down(*tile)
            if random.random() > .5:
                tile = invert_left(*tile)
            if i % 2 == 0:
                tile = invert_down(*tile)
            sprite = Sprite(*pos, tile)
            self.plates.append(sprite)

    def update(self):
        # todo: check whether a new tile needs to be rendered.
        pass

    def draw(self):
        for plate in self.plates:
            plate.draw()


class Player():
    '''
    The person playing the game.
    '''
    def __init__(self):
        self.x = 0
        self.y = 0
        self.assets = ((0, 0, 8, 8),  # N
                       (8, 0, 8, 8),  # NE
                       (0, 8, 8, 8),  # E
                       )
        self.pointing = random.randrange(9)
        logger.info("Beetle initialized at {}, {} pointing at {}.".format(
                    self.x, self.y, self.pointing))
        self.sprite = Sprite(self.x, self.y, *self.assets, transparent_color=7)
        self.game_location = []
        self.points = 0
        self.alive = True

    def rotate(self, direction):
        assert direction in (-1, 0, 1)  # counterclockwise, straight, clockwise
        self.pointing += direction
        self.pointing %= 8
        logger.info(f"Turning {direction} to {self.pointing}")

    def update(self):
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.point_asset(self.pointing)

    def walk(self, backwards=False):
        movement = advance(self.pointing, backwards=backwards)
        self.x += movement[0]
        self.y += movement[1]
        logger.info("Walking in {} direction to {}, {}".format(
                    movement, self.x, self.y))

    def draw(self):
        '''
        Draw the player's sprite.
        '''
        self.sprite.draw()


class App:
    '''
    Main game code.
    '''
    def __init__(self):
        pyxel.init(160, 120, caption="Beetle Charm")
        pyxel.load('assets/beetle-box.pyxel')
        self.player = Player()
        self.visible_map = VisibleMap()
        self.things = [self.visible_map, self.player]
        pyxel.playm(0, loop=True)

    def run(self):
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        elif pyxel.btnp(pyxel.KEY_W):
            self.player.walk()
        elif pyxel.btnp(pyxel.KEY_S):
            self.player.walk(backwards=True)
        elif pyxel.btnp(pyxel.KEY_A):
            self.player.rotate(-1)
        elif pyxel.btnp(pyxel.KEY_D):
            self.player.rotate(1)

        for objekt in self.things:
            objekt.update()

    def draw(self):
        '''
        Draw everything.
        '''
        pyxel.cls(1)
        for objekt in self.things:
            objekt.draw()


def main():
    a = App()
    logger.info("Beetle Charm loaded successfully.")
    a.run()
    logger.info("Thank you for playing.")


if __name__ == '__main__':
    main()
