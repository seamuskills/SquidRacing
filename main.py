import pygame

#compile again with the console command: auto-py-to-exe

sc = pygame.display.set_mode([540, 360], pygame.RESIZABLE | pygame.SCALED)
c = pygame.time.Clock()
dt = 0
scale = 1
quit = False

camera = pygame.Vector2(0, 0)

images = {
    "playerRipple": pygame.image.load("images/ripple.png"),
    "playerSquid": pygame.image.load("images/squid.png"),
    "testTrack": pygame.image.load("images/testTrack.png")
}

keys = []


def approach(x, y, amm):
    if x < y:
        return min(x + amm, y)
    if x > y:
        return max(x - amm, y)
    return y


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.vel = pygame.Vector2(0, 0)
        self.accel = 0.004
        self.maxSp = 0.25
        self.angle = 0
        self.submerged = True
        self.directionWanted = 0

    def update(self):
        self.submerged = sc.get_at([round(self.rect.x - camera.x), round(self.rect.y - camera.y)]) != pygame.color.Color((255, 255, 255))

        self.directionWanted = pygame.mouse.get_pressed(3)[0] - pygame.mouse.get_pressed(3)[2]
        move = (pygame.mouse.get_pos() + camera) - pygame.Vector2(self.rect.x,
                                                                  self.rect.y)  # the vector of where the player wants to move
        self.angle = move.angle_to(pygame.Vector2(1, 0))  # the angle this would make us face

        move *= self.directionWanted

        if move.magnitude() != 0: move = move.normalize()  # normalize the vector (unless its 0 because that causes an error)
        self.vel.x = approach(self.vel.x, move.x * self.maxSp, self.accel)  # multiply normalized vector by our acceleration amount and add it to velocity
        self.vel.y = approach(self.vel.y, move.y * self.maxSp, self.accel)
        # if self.vel.magnitude() != 0:
        #     self.vel.x = self.vel.x * min(self.vel.magnitude(),
        #                               self.maxSp) / self.vel.magnitude()  # set the mag of the velocity vector so it's never above maxSp
        #     self.vel.y = self.vel.y * min(self.vel.magnitude(), self.maxSp) / self.vel.magnitude()
        self.rect.x += (self.vel.x * dt) / (2 - self.submerged)  # add velocity to position keeping deltaTime in mind so it's frame rate independent
        self.rect.y += (self.vel.y * dt) / (2 - self.submerged)

        camera.x = self.rect.x - (sc.get_width() / 2)  # set camera position
        camera.y = self.rect.y - (sc.get_height() / 2)

    def draw(self):
        center = self.rect.copy()
        center.x -= center.w / 2
        center.y -= center.h / 2
        drawSprite = pygame.transform.rotate(images["playerRipple"], self.vel.angle_to(pygame.Vector2(1, 0)))
        if not self.submerged:
            drawSprite = pygame.transform.rotate(images["playerSquid"], self.angle)
        drawSprite.fill((255, 100, 0, 100), special_flags=pygame.BLEND_MULT)
        drawSprite = pygame.transform.scale(drawSprite,
                                            [drawSprite.get_width() * scale, drawSprite.get_height() * scale])
        if self.submerged:
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
    sc.fill([255, 255, 255])

    bg = pygame.transform.scale(images["testTrack"],
                                [images["testTrack"].get_width() * scale, images["testTrack"].get_height() * scale])
    bg.fill((130, 50, 0), special_flags=pygame.BLEND_MULT)
    sc.blit(bg, camera * -1)

    testPlayer.update()
    testPlayer.draw()

    pygame.display.flip()
    dt = c.tick(60)

    if quit:
        pygame.quit()
        break
