import math, pygame, json
from pygame.constants import K_r
pygame.init()

size = width, height = 1000, 600
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Fourier series 2")

running = True

FPS = 60
clock = pygame.time.Clock()
time = 0
points = []
tracePoints = []
centrepos = (200, 300)

vectors = []
isLoaded = False

showVectors = True
showVectorRadius = False
showGraph = True
showVectorGraphRelation = False
showVectorTrace = True

class waveFunction:
    def __init__(self, amplitude, frequency, function="sin", direction = 1):
        self.screen = pygame.display.get_surface()
        self.x = self.y = 0
        self.amplitude = amplitude
        self.frequency = frequency
        self.function = function
        self.direction = direction
    
    def update(self, pos, time):
        time = time * self.direction
        if self.function == "sin":
            self.x = pos[0] + (self.amplitude * math.cos(time * self.frequency))
            self.y = pos[1] + (self.amplitude * math.sin(time * self.frequency))
        elif self.function == "cos":
            self.x = pos[0] + (self.amplitude * math.sin(time * self.frequency))
            self.y = pos[1] + (self.amplitude * math.cos(time * self.frequency))

    def draw(self, pos, showRadius):
        if showRadius:
            pygame.draw.circle(self.screen, black, pos, self.amplitude, 1)
        pygame.draw.line(self.screen, blue, pos, (self.x, self.y))
    
    def getRadialPos(self):
        return (self.x, self.y)
    
    def setProperties(self, radius, frequency, function, direction):
        self.radius = radius
        self.frequency = frequency
        self.function = function
        self.direction = direction


def LoadVectors(filename="figeight.json"):
    global isLoaded
    global time
    global vectors
    oldvectors = vectors
    vectors.clear()
    time = 0
    #amplitudes = [50, 40, 35, 15, 10] # radius
    #frequencies = [1, 1, 2, 3, 3] # n
    #functions = ["sin", "sin", "sin", "sin", "sin"]
    #directions = [-1, 1, -1, 1, -1] # (anti)clockwise
    try:
        f = open("Functions/" + filename)
        data = json.loads(f.read())
        f.close()
        for v in data["vectors"]:
            vectors.append(waveFunction(v["amplitude"], v["frequency"], v["function"], v["direction"]))
        points.clear()
        tracePoints.clear()
        isLoaded = True
    except:
        vectors = oldvectors


# TODO: Add GUI to update curves

# TODO: Update curves while program running

#LoadVectors()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                LoadVectors("figeight2.json")

    screen.fill(white)

    if isLoaded == False:
        pygame.display.update()
        continue

    # -----------
    # Logic stuff


    # Draw all the rotating vectors
    vectors[0].update(centrepos, time)
    if showVectors:
        vectors[0].draw(centrepos, showVectorRadius)
    for v in range(1, len(vectors)):
        vectors[v].update(vectors[v-1].getRadialPos(), time)
        if showVectors:
            vectors[v].draw(vectors[v-1].getRadialPos(), showVectorRadius)

    # Add X positions to list
    points.insert(0, vectors[len(vectors)-1].getRadialPos()[1])
    if time <= 7:
        tracePoints.insert(0, vectors[len(vectors)-1].getRadialPos())

    # Trim list if it gets too long
    if len(points) > 500:
        points.pop()

    # Draw line between end of vectors and graph
    if showVectorGraphRelation:
        pygame.draw.line(screen, red, vectors[len(vectors)-1].getRadialPos(), (500, points[0]))

    # Draw graph
    if showGraph:
        for p in range(len(points)):
            if p > 0:
                pygame.draw.line(screen, green, (500 + p - 1, points[p-1]), (500 + p, points[p]))
    
    # Draw traced line
    if showVectorTrace:
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