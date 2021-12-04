import math, pygame
pygame.init()

size = width, height = 1000, 600
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Fourier series")

running = True

FPS = 60
clock = pygame.time.Clock()
time = 0
points = []
tracePoints = []
centrepos = (200, 300)

class rotatingVector:
    def __init__(self, radius):
        self.radius = radius
        self.screen = pygame.display.get_surface()
        self.x = self.y = 0

    def draw(self, pos, time, n):
        self.x = pos[0] + (self.radius * math.cos(time * n))
        self.y = pos[1] + (self.radius * math.sin(time * n))
        pygame.draw.circle(self.screen, black, pos, self.radius, 1)
        pygame.draw.line(self.screen, blue, pos, (self.x, self.y))
    
    def getRadialPos(self):
        return (self.x, self.y)

vectors = [] 
for i in range(8):
    n = i * 2 + 1
    vectors.append(rotatingVector(100 * (4 / (n * math.pi))))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(white)

    # -----------
    # Logic stuff


    # Draw all the rotating vectors
    vectors[0].draw(centrepos, time, 1)
    for v in range(1, len(vectors)):
        vectors[v].draw(vectors[v-1].getRadialPos(), time, v*2+1)

    # Add X positions to list
    points.insert(0, vectors[len(vectors)-1].getRadialPos()[1])
    if time <= 7:
        tracePoints.insert(0, vectors[len(vectors)-1].getRadialPos())

    # Trim list if it gets too long
    if len(points) > 500:
        points.pop()

    # Draw line between end of vectors and graph
    pygame.draw.line(screen, red, vectors[len(vectors)-1].getRadialPos(), (500, points[0]))

    # Draw graph
    for p in range(len(points)):
        if p > 0:
            pygame.draw.line(screen, green, (500 + p - 1, points[p-1]), (500 + p, points[p]))
    
    # Draw traced line
    for t in range(len(tracePoints)):
        if t > 0:
            pygame.draw.line(screen, green, tracePoints[t-1], tracePoints[t])



    # -----------------------------------------
    # Update display (MUST STAY AT END OF LOOP)
    pygame.display.update()

    time += 0.025
    clock.tick(FPS)


pygame.quit()
quit()