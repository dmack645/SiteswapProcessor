# diagramGenerator
"""
Need ladder node class. Contains beat coordinates and how many currently assigned ingoing throws
Each points to ingoing and outgoing terms.  
Circular structure
This might also take the form of a "validation structure". Links all throws together into orbits
load all thrownodes into structure, then set coordinates

load Ladder with throw values
load Ladder with coordinates (based on dwell, pixel/beat) (add length argument later - just do a complete cycle for now)
    first load self.vertex 
    sort incoming and outgoing throw lists smallest to largest. 
    Smaller valued outgoing throws should depart closer to boundary of ladder
    Smaller valued incoming throws should land closer to boundary of ladder
    then loop back through and load the catching coordinate for each outgoing throw
    

draw one orbit at a time.
"""
from siteswap import Siteswap
from throwNode import ThrowNode
from copy import deepcopy
from collections.abc import MutableSequence
from stateGenerator import StateGenerator
import turtle

class Ladder(): # MutableSequence (eventually). Needs __delitem__, __getitem__, __len__, __setitem__, insert

    def __init__(self):
        self.rushZips = True
        self.inLH = list()
        self.inRH = list()

        self.outLH = list()
        self.outRH = list()

        self.vertexLH = [0, 0]                  
        self.vertexRH = [0, 0]

        self.throwCoordsLH = list()  # lists of coordinate pairs 
        self.throwCoordsRH = list()

        self.catchCoordsLH = list()
        self.catchCoordsRH = list()


        self.next = self
        self.state = StateGenerator()       # Needed until I fix Siteswap.getMax()

        self.counterLH = 0                     # These count how many inbound throws have been "connected"
        self.counterRH = 0
        self.isRushed = False

    def load(self, siteswap, dwell, beatLength, jlabStr = ""):
        length = len(siteswap)
        self.jlabStr = jlabStr
        self.dwell = dwell
        siteswapProbe = siteswap
        ladderProbe = self
        index = 0

        # Load siteswap values into circular linked structure
        while index < length:
            if index != 0:
                temp = Ladder()
                temp.next = self
                ladderProbe.next = temp
                ladderProbe = ladderProbe.next
            for throw in siteswapProbe.left:
                ladderProbe.outLH.append([throw.throw, throw.throwX])
                ladderProbe.inLH.append([throw.rethrow, throw.rethrowX])
            ladderProbe.outLH.sort()
            ladderProbe.inLH.sort()
            for throw in siteswapProbe.right:
                ladderProbe.outRH.append([throw.throw, throw.throwX])
                ladderProbe.inRH.append([throw.rethrow, throw.rethrowX])
            ladderProbe.outRH.sort()
            ladderProbe.inRH.sort()
            siteswapProbe = siteswapProbe.next
            index += 1

        self.printDebug()
        
        self.state.generate(siteswap) # Required for getMax until fixed
        print("max:", siteswap.getMax())
        self.height = int(4 * beatLength)
        self.width = int((len(self) * beatLength) + (siteswap.getMax() * beatLength) + (2 * beatLength) + 10)
        if self.height % 2 != 0: self.height += 1
        self.beatLength = int(beatLength)           # pixels / beat
        self.spacing = int(0.1 * self.beatLength)
        self.dwellLength = int(dwell * self.beatLength)

        # Set vertex coordinates and throw coordinates
        self.markRushedThrows()
        length = len(self)
        probe = self
        index = 0
        xy = [0,0]

        # Load first vertex coordinates
        probe.vertexLH[0] = 0
        probe.vertexLH[1] = self.beatLength
        probe.vertexRH[0] = 0
        probe.vertexRH[1] = int(self.beatLength * -1)
        previousIsRushed = probe.isRushed
        if probe.isRushed:
            xy[0] += int(self.beatLength + (0.25 * self.dwellLength))   # make sure 1-d/4 and 1+d/4 add to 2 later
        else:
            xy[0] += self.beatLength
        index += 1
        probe = probe.next

        # Load the rest of the vertex coordinates
        while index < length:
            # If term doesn't only contain one "1" value throw, space vertex normally
            #elif not probe.isRushed():
            if not probe.isRushed:
                xy[0] += self.beatLength
                probe.vertexLH[0] = xy[0]
                probe.vertexLH[1] = self.beatLength
                probe.vertexRH[0] = xy[0]
                probe.vertexRH[1] = int(self.beatLength * -1)
            # I need to design this so even if the first term is a zip it'll be spaced properly
            else:
                probe.vertexLH[0] = xy[0]
                probe.vertexLH[1] = self.beatLength
                probe.vertexRH[0] = xy[0]
                probe.vertexRH[1] = int(self.beatLength * -1)                



            probe = probe.next
            index += 1

        screen = turtle.Screen()
        screen.setup(self.width, self.height) # LOOK AT PYTHON DOC - YOU CAN MAKE IT % OF SCREEN SIZE IF ARGUMENTS FLOAT
        screen.setworldcoordinates((self.beatLength * -2), self.beatLength * -2, self.width - (2 * self.beatLength), self.beatLength * 2)
        if self.jlabStr != "":
            title = "{} Diagram    Dwell: {} beats      Beat Length: {} pixels/beat".format(str(self.jlabStr), str(self.dwell), str(self.beatLength))
        else:
            title = "Siteswap Diagram    Dwell: {} beats      Beat Length: {} pixels/beat".format(str(self.dwell), str(self.beatLength))
        screen.title(title)
        pen = turtle.Turtle()
        pen.hideturtle()
        pen.penup()
        pen.goto(0,0)
        pen.dot(10, 'black')

        i = 0
        length = len(self)
        print(length)
        probe = self

        # Look at turtle.Vec2D class - might be useful
        while i < length:
            pen.left(90)
            pen.forward(self.beatLength)
            pen.dot(5, 'black')
            pen.right(180)
            pen.forward(self.beatLength *2)
            pen.dot(5, 'black')
            pen.left(180)
            pen.forward(self.beatLength)
            pen.right(90)
            pen.forward(self.beatLength)

            i += 1
        screen.exitonclick()


        
    def markRushedThrows(self):
        if not self.rushZips:
            return

        length = len(self)
        probe = self
        index = 0

        # Load vertex coordinates
        while index < length:
            if len(probe.outLH) == 1 and len(probe.outRH) == 0:
                if probe.outLH[0][0] == 1 and probe.outLH[0][1] == False:
                    probe.isRushed = True
            
            elif len(probe.outLH) == 0 and len(probe.outRH) == 1:
                if probe.outRH[0][0] == 1 and probe.outRH[0][1] == False:
                    probe.isRushed = True
            index += 1
            probe = probe.next

    def generate(self):
        pass

    def printDebug(self):
        #length = len(self)
        index = 0
        probe = self
        while index < len(self):
            print("\nTERM" + str(index) + ":  ", end = "")
            print("outLH: ", end = "")
            i = 0
            while i < len(probe.outLH):
                print(probe.outLH[i][0], end = "")
                if probe.outLH[i][1]:
                    print("x", end = "")
                print(" ", end = "")
                i += 1

            print("   inLH: ", end = "")
            i = 0
            while i < len(probe.inLH):
                print(probe.inLH[i][0], end = "")
                if probe.inLH[i][1]:
                    print("x", end = "")
                print(" ", end = "")
                i += 1

            print("   outRH: ", end = "")
            i = 0
            while i < len(probe.outRH):
                print(probe.outRH[i][0], end = "")
                if probe.outRH[i][1]:
                    print("x", end = "")
                print(" ", end = "")
                i += 1

            print("   inRH: ", end = "")
            i = 0
            while i < len(probe.inRH):
                print(probe.inRH[i][0], end = "")
                if probe.inRH[i][1]:
                    print("x", end = "")
                print(" ", end = "")
                i += 1

            index += 1
            probe = probe.next
                


    def __len__(self):
        probe = self
        length = 1

        while probe.next is not self:
            length += 1
            probe = probe.next
        return length  

    def __setitem__(self, index, value): # for getting list of coord lists
        pass

    def __getitem__(self, floor_number):
        pass


class DrawDiagram():
    def __init__(self):
        pass
    def generate(self, siteswap, length = 12, dwell = 1.3):
        self.siteswap = siteswap
        self.length = length
        self.dwell = dwell   
a = Ladder()
