import pyxel
import logging

logger = logging.Logger('Beetle Charm logger.')
logger.setLevel(logging.INFO)
logger.info('Beetle Charm initialized.')


class Sprite:
    '''
    Just somesprite.
    '''
    def __init__(self):
        self.x = 0
        self.y = 0
        self.asset_coords = [None] * 4

    def update(self):
        pass

    def draw(self):
        pass


class Player(Sprite):
    '''
    The person playing the game.
    '''
    def __init__(self):
        super().__init__()
        self.points = 0
        self.alive = True
        self.asset_coords = [4, 3, 8, 8]

    def draw(self):
        pyxel.blt(self.x, self.y, 0, *self.asset_coords)


class App:
    '''
    Main game code.
    '''
    def __init__(self):
        pyxel.init(160, 120, caption="Beetle Charm")
        pyxel.load('assets/beetle-box.pyxel')
        p = Player()
        self.sprites = [p]

        pyxel.playm(0, loop=True)
        logger.info("Beetle Charm loaded successfully.")
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        for objekt in self.sprites:
            objekt.draw()

    def draw(self):
        pass


def main():
    App()
    logger.info("Thank you for playing.")


if __name__ == '__main__':
    main()
