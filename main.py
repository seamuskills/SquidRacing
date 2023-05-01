import pygame
import pygame_menu
import os
import sys

#compile again with the console command:
# pyinstaller --noconfirm --onefile --windowed --add-data "C:/Users/James/PycharmProjects/SquidRacing/images;images/"  "C:/Users/James/PycharmProjects/SquidRacing/main.py"
# command generated via auto-py-to-exe

screenSize = [540, 360]

pygame.init()
sc = pygame.display.set_mode(screenSize, pygame.RESIZABLE | pygame.SCALED)
c = pygame.time.Clock()
dt = 0
scale = 1
quit = False
inkColor = pygame.Color(255, 100, 0)

camera = pygame.Vector2(0, 0)

def getPath(relative_path):
    base_path = ""
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

images = {
    "playerRipple": pygame.image.load(getPath("images/ripple.png")),
    "playerSquid": pygame.image.load(getPath("images/squid.png")),
    "playerCharge": pygame.image.load(getPath("images/chargedSquid.png")),
    "testTrack": pygame.image.load(getPath("images/testTrack.png")),
    "playerRoll": [
        pygame.image.load(getPath("images/roll/0.png")),
        pygame.image.load(getPath("images/roll/1.png")),
        pygame.image.load(getPath("images/roll/2.png")),
        pygame.image.load(getPath("images/roll/2.5.png")),
        pygame.image.load(getPath("images/roll/3.png")),
        pygame.image.load(getPath("images/roll/4.png"))
    ],
    "splatFont2": pygame.font.Font(getPath("images/Splatfont2.ttf"), 30),
    "splatFont1": pygame.font.Font(getPath("images/Splatoon1.otf"), 20)
}

keys = []

def darken(c, value=50):
    return c - pygame.Color(value, value, value)

def approach(x, y, amm):
    if x < y:
        return min(x + amm, y)
    if x > y:
        return max(x - amm, y)
    return y

menuTheme = pygame_menu.Theme(
    background_color=(255, 165, 0),
    title_background_color=(56, 56, 244),
    title_font_color=(255, 165, 0),
    title_font=images["splatFont2"],
    widget_font=images["splatFont1"],
    widget_font_color=(28, 28, 122),
    title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_TITLE_ONLY_DIAGONAL
)

def startGame():
    global menu
    menu.disable()
    menu = None

def options():
    global menu
    menu.disable()
    menu = optionsMenu
    menu.enable()

def optionsBack():
    global menu
    menu.disable()
    menu = mainMenu
    menu.enable()

def changeControls(k, v):
    if v == "arrow":
        pygame_menu.controls.KEY_MOVE_UP = pygame.K_s
        pygame_menu.controls.KEY_MOVE_DOWN = pygame.K_w
        pygame_menu.controls.KEY_RIGHT = pygame.K_d
        pygame_menu.controls.KEY_LEFT = pygame.K_a
    else:
        pygame_menu.controls.KEY_MOVE_UP = pygame.K_DOWN
        pygame_menu.controls.KEY_MOVE_DOWN = pygame.K_UP
        pygame_menu.controls.KEY_RIGHT = pygame.K_RIGHT
        pygame_menu.controls.KEY_LEFT = pygame.K_LEFT


def changeColor(v):
    global inkColor
    try:
        inkColor = pygame.Color(v[0], v[1], v[2])
    except:
        pass

mainMenu = pygame_menu.Menu("Squid Racing", theme=menuTheme, width=screenSize[0], height=screenSize[1])
mainMenu.add.button("Start", startGame)
mainMenu.add.button("Options", options)
mainMenu.add.button("Quit", pygame_menu.events.EXIT)
mainMenu.center_content()

optionsMenu = pygame_menu.Menu("Options", theme=menuTheme, width=screenSize[0], height=screenSize[1])
optionsMenu.add.color_input("ink color: ", pygame_menu.widgets.COLORINPUT_TYPE_RGB, default= (inkColor[0], inkColor[1], inkColor[2]), onchange=changeColor)
optionsMenu.add.selector("menu controls: ", [("arrow keys", "wasd"), ("wasd", "arrow")], onchange=changeControls)  #not sure why, but I must make it return the other option to the function or else the widget will display the control scheme that is not active.
optionsMenu.add.button("back", optionsBack)

menu = mainMenu

def getInked(pos):
    return sc.get_at(
        [round(pos[0] - camera.x), round(pos[1] - camera.y)]) != pygame.color.Color(
        (255, 255, 255))

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.vel = pygame.Vector2(0, 0)
        self.accel = 0.008
        self.maxSp = 0.3
        self.angle = 0
        self.submerged = True
        self.directionWanted = 0
        self.charge = 0
        self.chargeMax = 450
        self.cooldown = 0
        self.charging = False
        self.rolling = 0
        self.rollSpeed = 0

        # roll animation
        self.rollFrame = 0
        self.nextFrame = 50
        self.frameOrder = [0, 1, 2, 4, 5, 4, 3, 1, 0]  #  which image from the array of images is to be used next

    def update(self):
        self.submerged = False
        self.cooldown -= dt
        self.rolling -= dt
        if self.rolling:
            self.nextFrame -= dt
            if self.nextFrame <= 0:
                self.nextFrame = 50
                self.rollFrame += 1
                self.rollFrame %= len(self.frameOrder)

        self.directionWanted = (pygame.mouse.get_pressed(3)[0] - keys[pygame.K_SPACE]) * (self.charge < 150)
        move = (pygame.mouse.get_pos() + camera) - pygame.Vector2(self.rect.x,
                                                                  self.rect.y)  # the vector of where the player wants to move
        self.angle = move.angle_to(pygame.Vector2(1, 0))  # the angle this would make us face
        if move.magnitude() != 0: move = move.normalize()  # normalize the vector (unless its 0 because that causes an error)

        canRoll = abs(self.vel.angle_to((1,0)) - self.angle) > 80 and self.vel.magnitude() > (self.maxSp / 2) and self.rolling <= -50

        if canRoll and keys[pygame.K_SPACE]:
            self.rolling = 600
            self.rollSpeed = self.vel.magnitude()*0.86
            self.vel = move.copy()
            self.vel.scale_to_length(self.rollSpeed)
            self.rollFrame = 0
            self.nextFrame = 100

        if self.rolling > 0:
            move = self.vel.copy().normalize()
            self.vel.scale_to_length(self.rollSpeed)

        if pygame.mouse.get_pressed(3)[2] and self.cooldown <= 0 and not self.charging and self.rolling <= 0:
            self.charge += dt
            self.charge = min(self.charge,self. chargeMax * 1.1)
        else:
            if self.charge > 0:
                overInk = getInked([self.rect.x, self.rect.y])

                self.charging = True
                self.charge -= dt if overInk else dt / 4
                chargePercent = min(self.charge / self.chargeMax, 1)

                if self.charge > self.chargeMax * 0.6:
                    self.vel = move * self.maxSp * chargePercent * 2 / (1 if overInk else 1.5)
                else:
                    self.charging = False
                    self.charge = 0
                    self.cooldown = 1000
            else:
                self.submerged = sc.get_at(
                    [round(self.rect.x - camera.x), round(self.rect.y - camera.y)]) != pygame.color.Color(
                    (255, 255, 255))

        move *= self.directionWanted

        self.vel.x = approach(self.vel.x, move.x * (self.maxSp / (2 - (self.rolling > 0 or self.submerged))**2), self.accel * (2 - self.submerged)**2)  # multiply normalized vector by our acceleration amount and add it to velocity
        self.vel.y = approach(self.vel.y, move.y * (self.maxSp / (2 - (self.rolling > 0 or self.submerged))**2), self.accel * (2 - self.submerged)**2)
        # if self.vel.magnitude() != 0:
        #     self.vel.x = self.vel.x * min(self.vel.magnitude(),
        #                               self.maxSp) / self.vel.magnitude()  # set the mag of the velocity vector so it's never above maxSp
        #     self.vel.y = self.vel.y * min(self.vel.magnitude(), self.maxSp) / self.vel.magnitude()
        self.rect.x += (self.vel.x * dt)  # add velocity to position keeping deltaTime in mind so it's frame rate independent
        self.rect.y += (self.vel.y * dt)

        camera.x = self.rect.x - (sc.get_width() / 2)  # set camera position
        camera.y = self.rect.y - (sc.get_height() / 2)

    def draw(self):
        center = self.rect.copy()
        center.x -= center.w / 2
        center.y -= center.h / 2
        drawSprite = pygame.transform.rotate(images["playerRipple"], self.vel.angle_to(pygame.Vector2(1, 0)))
        if not self.submerged:
            drawSprite = pygame.transform.rotate(images["playerSquid"], self.angle)
            if self.charge > self.chargeMax:
                drawSprite = pygame.transform.rotate(images["playerCharge"], self.angle)
            elif not self.charging:
                chargePercent = 255 - (min(self.charge / self.chargeMax, 1) * 150)
                drawSprite.fill([chargePercent, chargePercent, chargePercent], special_flags=pygame.BLEND_MULT)

        if self.rolling >= 0:
            drawSprite = pygame.transform.rotate(images["playerRoll"][self.frameOrder[self.rollFrame]], self.vel.angle_to(pygame.Vector2(1, 0)))

        drawSprite.fill(inkColor, special_flags=pygame.BLEND_MULT)
        drawSprite = pygame.transform.scale(drawSprite,
                                            [drawSprite.get_width() * scale, drawSprite.get_height() * scale])
        if self.submerged and not self.rolling >= 0:
            speedPercent = (self.vel.magnitude() / self.maxSp)
            drawSprite = pygame.transform.scale(drawSprite, [drawSprite.get_width() * speedPercent, drawSprite.get_height() * speedPercent])
            drawSprite.set_alpha(speedPercent * 255)
        sc.blit(drawSprite, [(self.rect.x - camera.x) - (drawSprite.get_width() / 2),
                             (self.rect.y - camera.y) - (drawSprite.get_height() / 2)])
        # pygame.draw.rect(sc, [255, 100, 0], center)


testPlayer = Player(1, 1)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True

    keys = pygame.key.get_pressed()

    if menu is not None:
        menu.mainloop(sc)
        continue
    else:
        if keys[pygame.K_ESCAPE]:
            menu = mainMenu
            menu.enable()

    sc.fill([255, 255, 255])

    bg = pygame.transform.scale(images["testTrack"],
                                [images["testTrack"].get_width() * scale, images["testTrack"].get_height() * scale])
    bg.fill(darken(inkColor), special_flags=pygame.BLEND_MULT)
    sc.blit(bg, camera * -1)

    testPlayer.update()
    testPlayer.draw()

    pygame.display.flip()
    dt = c.tick(60)

    if quit:
        pygame.quit()
        break
