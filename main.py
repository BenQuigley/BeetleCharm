import logging
import pyxel
import random
import itertools

import pdb

logger = logging.getLogger("Beetle Charm logger")
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.info('Beetle Charm initialized.')


def invert_left(x, y, width, height):
    return (x, y, -1 * width, height)


def invert_down(x, y, width, height):
    return (x, y, width, -1 * height)


start = (16, 0, 8, 8)
assert invert_left(*start) == (16, 0, -8, 8)
assert invert_down(*start) == (16, 0, 8, -8)


def in_bounds(asset, bounds):
    '''
    :param coords: A 2-tuple of x, y coordinates.
    :param bounds: A 4-tuple: x, y, width, height.
    '''
    in_bounds_left = asset[0] >= bounds[0]
    in_bounds_right = asset[0] + asset[2] <= bounds[0] + bounds[2]
    in_bounds_up = asset[1] >= bounds[1]
    in_bounds_down = asset[1] + asset[3] <= bounds[1] + bounds[2]
    return all([in_bounds_left, in_bounds_right, in_bounds_up, in_bounds_down])


def eight_directions(n, ne, e):
    '''
    We can generate all eight directions if N, NE, and E are supplied.
    '''
    se = invert_down(*ne)
    s = invert_down(*n)
    sw = invert_left(*se)
    w = invert_left(*e)
    nw = invert_left(*ne)
    return [n, ne, e, se, s, sw, w, nw]


def build_asset_lib(asset):
    '''
    Return the following views of an asset, in order.
    :param n: the asset's north-facing view.
    :param ne: the asset's northeast-facing view.
    :param e: the asset's east-facing view.
    '''
    main = asset['main']
    alt = asset.get('alt') or ()
    if len(main) >= 3:
        asset['main'] = eight_directions(*main)
        if alt:
            asset['alt'] = eight_directions(*alt)
    return asset


def advance(direction: int, speed: int):
    '''
    With 0 being north, 2 east, 4 south, etc.,
    :return: (dx, dy) for the direction given.
    '''
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
    logger.info("Advancing in direction {}: dx= {}; dy={}".format(
                         direction, dx, dy))
    return (dx * speed, dy * speed)


class Sprite:
    '''
    Anything simple enough to be drawn just by blitting it to the screen.
    '''
    def __init__(self, x, y, single_asset=None, asset_lib=None,
                 transparent_color=0):
        '''
        :param asset: Expects a dict, but can handle a regular asset.
        '''
        self.x = x
        self.y = y
        if single_asset:
            asset_lib = {'main': [single_asset]}
        self.asset_key = 'main'
        self.asset_lib = build_asset_lib(asset_lib)
        self.asset = asset_lib['main'][0]
        self.trans = transparent_color

    def point_asset(self, direction):
        '''
        Return the correct asset coordinates for the direction the sprite is
        pointing.
        :param direction: Int between 0 and 8, with 0: N, 1: NE, etc.
        '''
        direction %= 8
        try:
            self.asset = self.asset_lib[self.asset_key][direction]
        except IndexError:
            pdb.set_trace()

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
            sprite = Sprite(*pos, single_asset=tile)
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
    def __init__(self, bounds):
        self.bounds = bounds
        self.x = random.randrange(bounds[0], bounds[2])
        self.y = random.randrange(bounds[1], bounds[3])
        self.assets = {
                       'main': [(0, 0, 8, 8),
                                (8, 0, 8, 8),
                                (0, 8, 8, 8)],
                       'alt': [(8, 8, 8, 8),
                               (0, 16, 8, 8),
                               (0, 24, 8, 8)],
                      }
        self.pointing = random.randrange(8)  # One of the eight directions.
        logger.info("Beetle initialized at {}, {} pointing at {}.".format(
                    self.x, self.y, self.pointing))
        self.sprite = Sprite(self.x, self.y, asset_lib=self.assets,
                             transparent_color=7)
        self.game_location = []
        self.speed = 0
        self.points = 0
        self.alive = True

    def rotate(self, direction):
        assert direction in (-1, 0, 1)  # counterclockwise, straight, clockwise
        self.pointing += direction
        self.pointing %= 8
        logger.info(f"Turning {direction} to {self.pointing}")

    def update(self):
        self.walk()
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.point_asset(self.pointing)

    def walk(self):
        movement = advance(self.pointing, self.speed)
        x = self.x + movement[0]
        y = self.y + movement[1]
        hypothetical_params = [x, y, self.sprite.asset[2],
                               self.sprite.asset[3]]
        if in_bounds(hypothetical_params, self.bounds):
            self.x = x
            self.y = y
            logger.info("Walking in {} direction to {}, {}".format(movement,
                        self.x, self.y))
        else:
            logger.info("Bumped into a wall.")

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
        bounds = (0, 0, 160, 120)
        pyxel.init(*bounds[2:], caption="Beetle Charm")
        pyxel.load('assets/beetle-box.pyxel')
        self.player = Player(bounds)
        self.visible_map = VisibleMap()
        self.things = [self.visible_map, self.player]
        pyxel.playm(0, loop=True)

    def run(self):
        pyxel.run(self.update, self.draw)

    def update(self):
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
