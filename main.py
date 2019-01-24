import logging
import pyxel
import random

logger = logging.Logger('Beetle Charm logger.')
logger.setLevel(logging.INFO)
logger.info('Beetle Charm initialized.')


class Sprite:
    '''
    Anything simple enough to be drawn just by blitting it to the screen.
    '''

    def __init__(self, x, y, asset_coords):
        self.x = x
        self.y = y
        self.asset_coords = asset_coords

    def draw(self):
        pyxel.blt(self.x, self.y, 0, *self.asset_coords)


class Plate(Sprite):
    pass


class VisibleMap:
    '''
    The map on which the game      +++++
    is played.                     +ooo+
    Drawable tiles:   +            +ooo+
    Drawn tiles:      o     Map:   +ooo+
    To be determined: -            +++++
    '''
    def __init__(self):
        self.coords = [0, 0, 90, 90]
        plate_assets = (
                         (16, 0, 8, 8),
                         (24, 0, 8, 8),
                         (16, 8, 8, 8),
                         (24, 8, 8, 8),
                        )
        screen_positions = [([i * 8, j * 8] for j in range(3)
                            for i in range(3))]
        self.plates = [Sprite(*pos, random.choice(plate_assets)) for pos in
                       screen_positions]

    def update(self):
        pass

    def draw(self):
        for plate in self.plates:
            plate.draw()


class Player(Sprite):
    '''
    The person playing the game.
    '''
    def __init__(self):
        super().__init__(x=0, y=0, asset_coords=[4, 3, 8, 8])
        self.game_location = []
        self.points = 0
        self.alive = True

    def update(self):
        pass

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
        self.things = [p]
        pyxel.playm(0, loop=True)

    def run(self):
        pyxel.run(self.update)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        for objekt in self.things:
            objekt.update()

    def draw(self):
        for objekt in self.things:
            objekt.draw()


def main():
    a = App()
    logger.info("Beetle Charm loaded successfully.")
    a.run()
    logger.info("Thank you for playing.")


if __name__ == '__main__':
    main()
