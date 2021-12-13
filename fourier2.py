import math, pygame, json, os, string, threading
from pygame.constants import K_r
import tkinter as tk
from tkinter import filedialog
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
paused = False
points = []
tracePoints = []
centrepos = (200, 300)

vectors = []
isFunctionLoaded = False
isEquationLoaded = False
currentFilename = ""

showVectors = True
showVectorRadius = True
showGraph = True
showVectorGraphRelation = True
showVectorTrace = True

# Class for wave functions/rotating vectors
class waveFunction:
    def __init__(self, amplitude, frequency, function="sin", direction = 1):
        self.screen = pygame.display.get_surface()
        self.x = self.y = 0
        self.amplitude = amplitude
        self.frequency = frequency
        self.function = function
        self.direction = direction
    
    # Updates the rotation of the vector
    def update(self, pos, time):
        time = time * self.direction
        if self.function == "sin":
            self.x = pos[0] + (self.amplitude * math.cos(time * self.frequency))
            self.y = pos[1] + (self.amplitude * math.sin(time * self.frequency))
        elif self.function == "cos":
            self.x = pos[0] + (self.amplitude * math.sin(time * self.frequency))
            self.y = pos[1] + (self.amplitude * math.cos(time * self.frequency))

    # Draws the rotating vector
    def draw(self, pos, showRadius):
        if showRadius:
            pygame.draw.circle(self.screen, black, pos, self.amplitude, 1)
        pygame.draw.line(self.screen, blue, pos, (self.x, self.y))
    
    # Gets the position on the radius of the vectors rotation
    def getRadialPos(self):
        return (self.x, self.y)
    
    # Sets the functions properties
    def setProperties(self, radius, frequency, function, direction):
        self.radius = radius
        self.frequency = frequency
        self.function = function
        self.direction = direction

    def ParseEquation(self, equation, n):
        a = frequency = 0
        function = ""
        direction = 1

        e = []

        currentNumber = ""
        currentLetter = ""
        lastItem = ""
        # Break down string into array of operations
        for i in equation:
            if i in map(str, list(range(10))):
                #print("number")
                currentNumber += i
                if lastItem == "L":
                    e.append(currentLetter)
                    currentLetter = ""
                lastItem = "N"
            elif i in string.ascii_lowercase:
                #print("letter")
                currentLetter += i
                if lastItem == "N":
                    e.append(currentNumber)
                    currentNumber = ""
                lastItem = "L"
            elif i in ["(", ")"]:
                #print("Bracket")
                if lastItem == "L":
                    e.append(currentLetter)
                    currentLetter = ""
                elif lastItem == "N":
                    e.append(currentNumber)
                    currentNumber = ""
                e.append(i)
                lastItem = "B"
            elif i in ["+", "-", "*", "/", "^"]:
                #print("Operator")
                if lastItem == "L":
                    e.append(currentLetter)
                    currentLetter = ""
                elif lastItem == "N":
                    e.append(currentNumber)
                    currentNumber = ""
                e.append(i)
                lastItem = "O"
            elif i == " ":
                if lastItem == "L":
                    e.append(currentLetter)
                    currentLetter = ""
                elif lastItem == "N":
                    e.append(currentNumber)
                    currentNumber = ""
                lastItem = ""
        
        print(e)
        self.amplitude = float(self.Evaluate(e, n)) * 20
        if self.amplitude < 0:
            self.direction = -1
        # Brackets pass

        # Division pass
        # Multiplication pass
        # Addition pass
        # Subtraction pass
        # etc...

        return (a, frequency, function, direction)

    # Evaluates an expression given as an array
    def Evaluate(self, expression, n):
        #print("Evaluating " + "','".join(expression))
        newExpression = []
        depth = 0
        toEvaluate = []
        if len(expression) == 0:
            return ""

        if "(" in expression or ")" in expression:
            for i in expression:
                if depth >= 1:
                    toEvaluate.append(i)
                else:
                    if i != "(" and i != ")":
                        newExpression.append(i)
                
                if i == "(":
                    depth += 1
                if i == ")":
                    depth -= 1
                    if depth == 0:
                        toEvaluate.pop()
                        result = self.Evaluate(toEvaluate, n)
                        if result != "":
                            newExpression.append(result)
                        toEvaluate.clear()
        else:
            newExpression = expression

        print("Evaluating" + "','".join(newExpression))

        if len(newExpression) == 1:
            if newExpression[0] == "x":
                self.frequency = 1
            return newExpression[0]
        
        lhs = newExpression[0]
        rhs = operator = ""
        try:
            rhs = str(float(newExpression[1]))
            operator = "*"
        except:
            if newExpression[1] in ["sin", "cos"]:
                operator = "*"
                rhs = newExpression[1]
            else:
                operator = newExpression[1]
                rhs = newExpression[2]
        
        if lhs == "n":
            lhs = n
        
        if rhs == "n":
            rhs = n

        if rhs == "x":
            self.frequency = lhs
            return ""
        
        if lhs == "x":
            self.frequency = rhs
            return ""

        if rhs in ["sin", "cos"]:
            self.function = rhs
            return lhs

        returnValue = 0
        if operator == "/":
            returnValue = float(lhs) / float(rhs)
        elif operator == "*":
            returnValue = float(lhs) * float(rhs)
        elif operator == "+":
            returnValue = float(lhs) + float(rhs)
        elif operator == "-":
            returnValue = float(lhs) - float(rhs)
        elif operator == "^":
            returnValue = math.pow(float(lhs), float(rhs))
        
        return str(returnValue)


# Amplitude = Radius
# Frequency = speed
# Function = Sin/Cos
# Direction = Clockwise/Anticlockwise

def LoadVectors(reload=True):
    global isFunctionLoaded
    global time
    global vectors
    global currentFilename
    oldvectors = vectors
    vectors.clear()
    time = 0
    try:
        if reload == False:
            currentFilename = filedialog.askopenfilename(filetypes=(("json files", "*.json"), ("All files", "*.*")),
                title="Open file",
                initialdir=os.getcwd())
        f = open(currentFilename)
        data = json.loads(f.read())
        f.close()
        for v in data["vectors"]:
            vectors.append(waveFunction(v["amplitude"], v["frequency"], v["function"], v["direction"]))
        points.clear()
        tracePoints.clear()
        isFunctionLoaded = True
    except:
        vectors = oldvectors


def LoadEquation(accuracy=10, reload=True):
    global isEquationLoaded
    global time
    global vectors
    global currentFilename
    oldvectors = vectors
    vectors.clear()
    time = 0
    try:
        if reload == False:
            currentFilename = filedialog.askopenfilename(filetypes=(("wave files", "*.wave"), ("All files", "*.*")),
                title="Open file",
                initialdir=os.getcwd())
        f = open(currentFilename)
        data = f.read()
        f.close()
        for n in range(1, accuracy):
            wave = waveFunction(0, 0)
            wave.ParseEquation(data, n)
            vectors.append(wave)
            continue
            # r = n * 2 + 1 Square
            r = eval(data["equation"]["amplitude"]) # Really bad practice, REMOVE ASAP
            vectors.append(waveFunction(40 * r,
            eval(data["equation"]["frequency"]),
            data["equation"]["function"],
            eval(data["equation"]["direction"])))
        points.clear()
        tracePoints.clear()
        isEquationLoaded = True
    except:
        vectors = oldvectors






# TODO: Add GUI to update curves

# TODO: Update curves while program running

# Hide tkinter window
root = tk.Tk()
root.withdraw()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Reload file
            if event.key == pygame.K_r:
                if isFunctionLoaded:
                    LoadVectors(True)
                elif isEquationLoaded:
                    LoadEquation(100, True)
            # Open file
            elif event.key == pygame.K_o:
                LoadVectors(False)
            # Open function
            elif event.key == pygame.K_f:
                LoadEquation(100, False)
            # pause
            elif event.key == pygame.K_p:
                paused = not paused
    screen.fill(white)

    # Only continue if file is open
    if isFunctionLoaded == False and isEquationLoaded == False:
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

    if not paused:
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

    if not paused:
        time += 0.025
    clock.tick(FPS)


pygame.quit()
quit()