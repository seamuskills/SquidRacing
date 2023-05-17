import pygame
import pygame_menu
import os
import sys
import colorsys
#compile again with the console command:
# pyinstaller --noconfirm --onefile --windowed --add-data "./images;images/"  "./main.py"
# command generated via auto-py-to-exe

screenSize = [540, 360]

pygame.init()
sc = pygame.display.set_mode(screenSize, pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Squid Racing    loading")
c = pygame.time.Clock()
dt = 0
quit = False
inkColor = pygame.Color(255, 100, 0)
mode = 0  # 0 = test, 1 = time trial?, 2 = race ai?
cameraStyle = 0  # 0 = player centered, 1 = dynamic

bgEnemy = 0
bgAlly = 0
bgJump = 0

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
    "damageOverlay": pygame.image.load(getPath("images/inkOverlay.png")),
    "playerRoll": [
        pygame.image.load(getPath("images/roll/0.png")),
        pygame.image.load(getPath("images/roll/1.png")),
        pygame.image.load(getPath("images/roll/2.png")),
        pygame.image.load(getPath("images/roll/2.5.png")),
        pygame.image.load(getPath("images/roll/3.png")),
        pygame.image.load(getPath("images/roll/4.png"))
    ],
    "spawnDrone": pygame.image.load(getPath("images/drone.png")),
    "respawnArrow": pygame.image.load(getPath("images/respawnArrow.png")),
    "tracks": {  # format: [ally ink, enemy ink]
        "test": {
            "images": [pygame.image.load(getPath("images/testTrack.png")).convert_alpha(), pygame.image.load(getPath("images/testTrackEnemy.png")).convert_alpha(), pygame.image.load(getPath("images/testTrackJump.png")).convert_alpha()],
            "spawn": [122, 346],
            "displayName": "testing grounds"
        }
    },
    "splatFont2": pygame.font.Font(getPath("images/Splatfont2.ttf"), 30),
    "splatFont1": pygame.font.Font(getPath("images/Splatoon1.otf"), 20)
}

pygame.display.set_icon(images["playerSquid"])

track = None

keys = []

def getDarkened(c, value=50):
    return c - pygame.Color(value, value, value, 0)

def getInvert(c):
    invert = pygame.Color(255, 255, 255) - c
    invert.a = 255
    return invert

def getAdjecent(c):
    color = c.hsva
    color = colorsys.hsv_to_rgb(((color[0] + 50) % 360) / 360, color[1]/100, color[2]/100)
    color = [color[0]*255, color[1]*255, color[2]*255]
    return pygame.Color(color)

overlay = images["damageOverlay"].convert_alpha()
overlay.fill(getInvert(inkColor), special_flags=pygame.BLEND_MULT)

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

def cameraControl(k, v):
    global cameraStyle
    cameraStyle = v

def changeColor(v):
    global inkColor
    global overlay
    try:
        inkColor = pygame.Color(v[0], v[1], v[2])
        recolorStage(inkColor)
        overlay = images["damageOverlay"].convert_alpha()
        overlay.fill(getInvert(inkColor), special_flags=pygame.BLEND_MULT)
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
optionsMenu.add.selector("camera system: ", [("player centered", False), ("direction dynamic", True)], onchange=cameraControl)
optionsMenu.add.button("back", optionsBack)

menu = mainMenu

def getInked(pos):
    try:
        color = sc.get_at(
        [round(pos[0] - camera.x), round(pos[1] - camera.y)])
    except:
        return 0
    if color == inkColor or color == getDarkened(inkColor):  # player color
        return 1
    if color == getInvert(inkColor) or color == getDarkened(getInvert(inkColor)):  # enemy color
        return -1
    if color == getAdjecent(inkColor) or color == getDarkened(getAdjecent(inkColor)):  # jump pad color
        return 2
    return 0

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
        self.maxRoll = 600

        # roll animation
        self.rollFrame = 0
        self.nextFrame = 50
        self.frameOrder = [0, 1, 2, 4, 5, 4, 3, 1, 0]  #  which image from the array of images is to be used next

        self.health = 500
        self.maxHealth = 500
        self.rollMove = pygame.Vector2(0, 0)
        self.dead = False
        self.respawnTime = 0
        self.maxRespawn = 5000
        self.dronePos = pygame.Vector2(0, 0)
        self.droneTime = 0
        self.maxDroneTime = 2500
        self.droneLaunch = 1200
        self.lastSafePos = pygame.Vector2(x, y)
        self.droneDir = 0

    def update(self):
        self.submerged = False
        self.cooldown -= dt
        self.rolling -= dt
        self.droneTime -= dt

        if getInked([self.rect.x, self.rect.y]) == 1 or getInked([self.rect.x, self.rect.y]) == 0:
            self.lastSafePos = pygame.Vector2(self.rect.x, self.rect.y)

        if self.dead:
            if self.droneLaunch > self.droneTime > 0:
                move = ((pygame.mouse.get_pos() + camera) - self.dronePos)
                self.dead = False
                self.rolling = 500
                self.rollSpeed = self.maxSp
                self.vel = move.copy()
                self.vel.scale_to_length(self.rollSpeed)
                self.rollFrame = 0
                self.nextFrame = 100
                self.rollMove = move.copy()
                self.rect = pygame.rect.Rect(self.dronePos.x, self.dronePos.y, self.rect.w, self.rect.h)

            if self.droneTime > 0:
                camera.x = self.dronePos.x - (sc.get_width() / 2)  # set camera position
                camera.y = self.dronePos.y - (sc.get_height() / 2)
                if self.droneTime > self.droneLaunch:
                    self.droneDir = ((pygame.mouse.get_pos() + camera) - self.dronePos).angle_to([1, 0])

            self.respawnTime -= dt
            if self.respawnTime <= 0 and self.droneTime < 0:
                self.health = self.maxHealth
                self.vel.x = 0
                self.vel.y = 0
                self.droneTime = self.maxDroneTime
                self.dronePos = self.lastSafePos.copy()
            else:
                return

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
            self.rolling = self.maxRoll
            self.rollSpeed = self.vel.magnitude()*0.86
            self.vel = move.copy()
            self.vel.scale_to_length(self.rollSpeed)
            self.rollFrame = 0
            self.nextFrame = 100
            self.rollMove = self.vel.copy().normalize()

        if getInked([self.rect.x, self.rect.y]) == 2 and self.rolling < -200 and self.vel.magnitude() > 0:
            self.rolling = self.maxRoll * 1.5
            self.rollSpeed = self.vel.magnitude() * 0.9
            self.vel = move.copy()
            self.vel.scale_to_length(self.rollSpeed)
            self.rollFrame = 0
            self.nextFrame = 100
            self.rollMove = move.copy()

        if self.rolling > 0 and self.vel.magnitude() > 0:
            move = self.rollMove.copy()
            self.vel.scale_to_length(self.rollSpeed)

        if pygame.mouse.get_pressed(3)[2] and self.cooldown <= 0 and not self.charging and self.rolling <= 0:
            self.charge += dt
            self.charge = min(self.charge,self. chargeMax * 1.1)
        else:
            if self.charge > 0:
                overInk = getInked([self.rect.x, self.rect.y])

                self.charging = True
                self.charge -= dt if overInk == 1 else dt / 4
                chargePercent = min(self.charge / self.chargeMax, 1)

                if self.charge > self.chargeMax * 0.6:
                    self.vel = move * self.maxSp * chargePercent * 2 / (1 if overInk == 1 else 1.5)
                else:
                    self.charging = False
                    self.charge = 0
                    self.cooldown = 1000
            else:
                self.submerged = getInked([self.rect[0], self.rect[1]]) == 1

        if self.rolling <= 0: move *= self.directionWanted

        if self.rolling <= 0: self.vel.x = approach(self.vel.x, move.x * (self.maxSp / (2 - (self.rolling > 0 or self.submerged))**2), self.accel * (2 - self.submerged)**2)  # multiply normalized vector by our acceleration amount and add it to velocity
        if self.rolling <= 0: self.vel.y = approach(self.vel.y, move.y * (self.maxSp / (2 - (self.rolling > 0 or self.submerged))**2), self.accel * (2 - self.submerged)**2)
        # if self.vel.magnitude() != 0:
        #     self.vel.x = self.vel.x * min(self.vel.magnitude(),
        #                               self.maxSp) / self.vel.magnitude()  # set the mag of the velocity vector so it's never above maxSp
        #     self.vel.y = self.vel.y * min(self.vel.magnitude(), self.maxSp) / self.vel.magnitude()
        self.rect.x += (self.vel.x * dt)  # add velocity to position keeping deltaTime in mind so it's frame rate independent
        self.rect.y += (self.vel.y * dt)

        if getInked([self.rect.x, self.rect.y]) == -1 and self.rolling <= 0:
            self.health -= dt
            self.charge = 0
            self.charging = False
            self.cooldown = 0
            if self.health <= 0:
                self.dead = True
                self.respawnTime = self.maxRespawn
                self.droneTime = 0
        else:
            self.health += dt / 2
            self.health = min(self.health, self.maxHealth)

        screenMouse = pygame.mouse.get_pos() + camera

        camera.x = self.rect.x - (sc.get_width() / 2) if cameraStyle == 0 else ((self.rect.x + screenMouse[0]) / 2) - (sc.get_width() / 2)  # set camera position
        camera.y = self.rect.y - (sc.get_height() / 2) if cameraStyle == 0 else ((self.rect.y + screenMouse[1]) / 2) - (sc.get_height() / 2)

    def drawDrone(self):
        if self.droneTime > 0:
            drone = images["spawnDrone"].copy()
            drone = pygame.transform.rotate(drone, self.droneDir)

            sc.blit(drone, [(self.dronePos.x - camera.x - drone.get_width()/2), (self.dronePos.y - camera.y - drone.get_height()/2)])

    def draw(self):
        damage = overlay
        damage.set_alpha(round((1- (self.health / self.maxHealth))*255))
        sc.blit(damage, [0, 0])
        if self.dead:
            if self.droneTime <= 0:
                respawnPercent = self.respawnTime / self.maxRespawn
                arrow = images["respawnArrow"].copy()
                arrowTint = arrow.copy()
                arrowTint.fill(inkColor, special_flags=pygame.BLEND_MULT)
                sc.blit(arrowTint, [screenSize[0] * 0.8, screenSize[1] * 0.75])
                sc.blit(arrow, [screenSize[0] * 0.8, screenSize[1] * 0.75], [0, 0, arrow.get_width() * respawnPercent, arrow.get_height()])
            self.drawDrone()
            return
        # center = self.rect.copy()
        # center.x -= center.w / 2
        # center.y -= center.h / 2
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
        if self.submerged and not self.rolling >= 0:
            speedPercent = (self.vel.magnitude() / self.maxSp)
            drawSprite = pygame.transform.scale(drawSprite, [drawSprite.get_width() * speedPercent, drawSprite.get_height() * speedPercent])
            drawSprite.set_alpha(speedPercent * 255)
        sc.blit(drawSprite, [(self.rect.x - camera.x) - (drawSprite.get_width() / 2),
                             (self.rect.y - camera.y) - (drawSprite.get_height() / 2)])
        # pygame.draw.rect(sc, [255, 100, 0], center)
        self.drawDrone()


player = Player(1, 1)
track = images["tracks"]["test"]

def recolorStage(c):
    global bgEnemy
    global bgAlly
    global bgJump
    bgEnemy = track["images"][1].copy()
    bgEnemy.fill(getDarkened(getInvert(c)), special_flags=pygame.BLEND_MULT)

    bgAlly = track["images"][0].copy()
    bgAlly.fill(getDarkened(c), special_flags=pygame.BLEND_MULT)

    bgJump = track["images"][2].copy()
    bgJump.fill(getAdjecent(c), special_flags=pygame.BLEND_MULT)

recolorStage(inkColor)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True

    keys = pygame.key.get_pressed()

    if menu is not None:
        pygame.display.set_caption("Squid Racing    Menu")
        menu.mainloop(sc)
        dt = 0
        continue
    else:
        pygame.display.set_caption("Squid Racing    " + track["displayName"])
        if keys[pygame.K_ESCAPE]:
            menu = mainMenu
            menu.enable()

    sc.fill([255, 255, 255])

    sc.blit(bgEnemy, camera * -1)
    sc.blit(bgAlly, camera * -1)
    sc.blit(bgJump, camera * -1)

    player.update()
    player.draw()

    pygame.display.flip()
    dt = c.tick(60)

    if quit:
        pygame.quit()
        break
