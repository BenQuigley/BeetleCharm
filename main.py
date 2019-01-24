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


class Sprite:
    '''
    Anything simple enough to be drawn just by blitting it to the screen.
    '''
    def __init__(self, x, y, asset_coords, trans=0):
        self.x = x
        self.y = y
        self.asset_coords = asset_coords
        self.trans = trans

    def draw(self):
        pyxel.blt(self.x, self.y, 0, *self.asset_coords, self.trans)


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
        for pos in screen_positions:
            sprite = Sprite(*pos, random.choice(plate_assets))
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
        self.assets = ((0, 0, 8, 8),    # N
                       (8, 0, 8, 8),    # NE
                       (0, 8, -8, -8),  # E
                       (8, 0, -8, -8),  # SE
                       (0, 8, 8, -8),   # S (8, 8, 8, -8),   # SW
                       (8, 8, -8, -8),  # W
                       (8, 0, -8, -8),  # NW
                       )
        self.turn = random.randrange(len(self.assets))  # 1: N, 2: NE
        self.pointing = [random.randrange(-1, 2) for _ in range(2)]
        logger.info("Beetle initialized at {}, {} pointing at {}.".format(
                    self.x, self.y, self.pointing))
        self.sprite = Sprite(self.x, self.y, self.asset_coords, trans=7)
        self.game_location = []
        self.points = 0
        self.alive = True

    @property
    def asset_coords(self):
        '''
        Return the correct asset coordinates for the direction the player is
        pointing.
        '''
        return self.assets[self.turn]

    def update(self):
        # todo turn sprite
        pass

    def rotate(self, direction):
        assert direction in (-1, 0, 1)  # counterclockwise, straight, clockwise
        self.turn += direction

    def walk(self, direction='forwards'):
        if direction == 'forwards':
            self.x += self.pointing[0]
            self.y += self.pointing[1]
        elif direction == 'backwards':
            self.x -= self.pointing[0]
            self.y -= self.pointing[1]

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
            self.player.walk('backwards')
        elif pyxel.btnp(pyxel.KEY_A):
            self.player.rotate(-1)
        elif pyxel.btnp(pyxel.KEY_A):
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
