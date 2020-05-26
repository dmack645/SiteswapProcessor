from siteswapParser import Parser
from siteswap import Siteswap
from siteswapValidator import SiteswapValidator
from stateGenerator import StateGenerator
from throwNode import ThrowNode
import os
import webbrowser
from copy import deepcopy

class SiteswapHandler(object):
    def __init__(self):
        self.siteswap = Siteswap()
        self.validator = SiteswapValidator()
        self.stateGenerator = StateGenerator()

    # Input format: swap 0r0 3l1
    # make sure to pass integers
    # Add function to clear zeroes out of multiplex throws

    def swap(self, siteswapOriginal, term1Index, hand1, throw1Index, term2Index, hand2, throw2Index):
        # Instead, I'll add a method to delete a given throwNode after gettting its information
        # I can also add an insertThrow method to insert new values in correct spot
        # Get pointers to indicated terms
        siteswap = deepcopy(siteswapOriginal)
        siteswap.clearRethrowValues()
        term1 = siteswap.getTerm(term1Index)  # pointer
        term2 = siteswap.getTerm(term2Index)  # pointer
        #print(siteswap)

        # Get pointers to throwNode structures of indicated throws to swap
        if hand1 == 'r':
            throw1 = term1.right             # pointer
            throw1Head = throw1
        else:
            throw1 = term1.left
            throw1Head = throw1
        if hand2 == 'r':
            throw2 = term2.right
            throw2Head = throw2
        else:
            throw2 = term2.left
            throw2Head = throw2

        #throw1Length = len(throw1)
        #throw2Length = len(throw2)

        # Point each to correct throw in throwNode structure (null-terminated)
        # Add empty throw if index greater than throw structure length
        i = throw1Index
        while i != 0 and throw1.next != None:
            throw1 = throw1.next
            i -= 1

        if i >= 1:
            zeroThrow = ThrowNode(0, False)
            throw1Head.addThrow(zeroThrow)
            if len(throw1Head) != 1:
                throw1 = throw1.next
            throw1Index = len(throw1Head) - 1

        i = throw2Index
        while i != 0 and throw2.next != None:
            throw2 = throw2.next
            i -= 1

        if i >= 1:
            zeroThrow = ThrowNode(0, False)
            throw2Head.addThrow(zeroThrow)
            if len(throw2Head) != 1:
                throw2 = throw2.next
            throw2Index = len(throw2Head) - 1
        

        # Get throw values, throwX, and throw parity if not null
        value1 = throw1.throw
        x1 = throw1.throwX
        if value1 == None: value1 = 0

        value2 = throw2.throw
        x2 = throw2.throwX
        if value2 == None: value2 = 0


        # I can delete original throw nodes now
        throw1Head.deleteThrow(throw1Index)
        throw2Head.deleteThrow(throw2Index)

        # Get relative difference between terms and parity of difference
        if term2Index - term1Index >= 0:
            difference = term2Index -term1Index
        else:
            difference = (term2Index - term1Index) + len(siteswap)
        diffParity = (difference % 2 == 0)


        '''
        print("value 1:",value1)
        print("x1:", x1)
        print("value 2:",value2)
        print("x2:", x2)
        print("difference:", difference)
        '''

        # Adjust values (downright rule), get parity of difference    
        newValue1 = value1 - difference
        newValue2 = value2 + difference

        if newValue1 < 0 or newValue2 < 0:
            print("Error: resulting values of swap function can't be negative.")
            return siteswapOriginal

        # If difference between terms is odd, switch X values (unless original null or 0)
        if diffParity == False: 
            newX1 = not x1
            newX2 = not x2  
        else:
            newX1 = x1
            newX2 = x2    
 
        # If swapping RH throw with LH throw, switch X values again (unless original null or 0)
        if hand1 != hand2:
            newX1 = not newX1
            newX2 = not newX2 

        '''
        print("newValue 1:",newValue1)
        print("newX1:", newX1)
        print("newValue 2:",newValue2)
        print("newX2:", newX2)
        print("siteswap to be modified:", str(siteswap))
        print("throw1:", throw1)
        print("throw2:", throw2)
        '''

        throw1Head.insertThrow(ThrowNode(newValue2, newX2), throw1Index)
        throw2Head.insertThrow(ThrowNode(newValue1, newX1), throw2Index)

        #print("siteswap after modification:", str(siteswap))
        self.validate(siteswap)
        return siteswap

    def parseString(self, string, quiet = True):
        tempSiteswap = Siteswap()
        parser = Parser()               

        try:
            tempSiteswap = parser.parse(string)
            #siteswap.printSiteswap()
        except Exception as e:
            if quiet == False:
                print("Error:")
                print(e)
            return False 
        return tempSiteswap

    def validate(self, siteswap):
        self.siteswap = siteswap
        return self.validator.validate(siteswap)

    def shift(self, siteswap, direction):
        if siteswap.isEmpty() or len(siteswap) == 1:
            return
        elif direction == 'sl':
            self.validate(siteswap.next)
            return siteswap.next

        else:
            self.validate(siteswap.getTerm(len(siteswap) - 1))
            return siteswap.getTerm(len(siteswap) - 1)
        return
           
    def getTextFilesDict(self):
        fileList = os.listdir()
        textList = list()
        for fileName in fileList:
            if '.txt' in fileName:
                file = open(fileName)
                if len(self.getSiteswapDict(file)) != 0:
                    textList.append(fileName)
                file.close()

        if len(textList) == 0:
            return(dict())
        else:
            return {i + 1 : textList[i] for i in range(0, len(textList))}

    def getSiteswapDict(self, file):
        siteswapList = list()
        for string in file:
            if self.parseString(string) != False:
                if not self.parseString(string).isEmpty():
                    siteswapList.append(string)

        if len(siteswapList) == 0:
            return(dict())
        else:
            return {i + 1 : siteswapList[i].rstrip() for i in range(0, len(siteswapList))}

    def writeStrToFile(self, string, fileName):
        if os.path.exists(fileName):
            string = '\n' + string

        file = open(fileName, 'a+')
        file.write(string)
        file.close()

    def generateStates(self, siteswap):
        self.stateGenerator.generate(siteswap)

    def getVanillaFirstHand(self, siteswap): 
        index = 0
        length = len(siteswap)

        while index < length:
            if siteswap.left.isNull() and not siteswap.right.isNull():
                return 'r'
            elif siteswap.right.isNull() and not siteswap.left.isNull():
                return 'l'
            siteswap = siteswap.next 
            index += 1
        return 'r'

    def getVanillaFirstIndex(self, siteswap):
        index = 0
        length = len(siteswap)

        while index < length:
            if siteswap.left.isNull() and siteswap.right.isNull():
                siteswap = siteswap.next 
                index += 1
            else:
                return index


        return 0

    def drawDiagram(self, siteswap, dwell = 0):
        pass




    def getSimpleString(self, siteswap = 0, mhn = False, asterisk = False):
        """Returns a string representation of the structure in MHN format"""
        if siteswap == 0:
            siteswap = self.siteswap

        if siteswap.isVanilla() and not mhn:
            return self.getJlabString(siteswap)
        else:
            string = ""

            index = 0
            probe = siteswap
            
            if asterisk == True and siteswap.isSymmetric():
                length = len(siteswap) // 2
            else:
                length = len(siteswap)

            while index < length:
                string += ("(%s,%s)" % (probe.left.getSimpleString(), probe.right.getSimpleString()))
                probe = probe.next
                index += 1
            if asterisk == True and siteswap.isSymmetric():
                string += "*"
            return string

    def getJlabString(self, siteswap = 0): 
        """Returns a string representation of the structure in JLAB format"""
        if siteswap == 0:
            siteswap = self.siteswap

        string = ""
        index = 0


        if siteswap.isVanilla():
            hand = self.getVanillaFirstHand(siteswap)
            firstIndex = self.getVanillaFirstIndex(siteswap)

            # get first term hand 
            while firstIndex != 0:
                firstIndex -= 1
                if hand == 'r':
                    hand = 'l'
                else:
                    hand = 'r'

            if siteswap.isSymmetric(): # SHOULDN'T NEED .SYMMETRIC. JUST ISSYMMETRIC IN HANDLER~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                patternLength = len(siteswap) // 2
            else:
                patternLength = len(siteswap)

            probe = siteswap
            while index < patternLength:
                if hand == 'r':
                    if str(probe.right) == '-':
                        value = '0'
                    else:
                        value = str(probe.right)
                    string += value
                    hand = 'l'
                else:
                    if str(probe.left) == '-':
                        value = '0'
                    else:
                        value = str(probe.left)
                    string += value
                    hand = 'r'
                index += 1
                probe = probe.next
            return string

        elif siteswap.isSimpleSync():
            probe = siteswap
            # point to first term that isn't a null beat
            while True:
                if probe.left.throw != None or probe.right.throw != None:
                    break
                probe = probe.next

            throwBeat = True
            index = 0
            if siteswap.isSymmetric():
                length = len(siteswap) // 2
            else:
                length = len(siteswap)
            while index < length:
                if not throwBeat:
                    probe = probe.next
                    index += 1
                    throwBeat = True
                    continue
                if probe.left.getSimpleString() == '-':
                    left = '0'
                else:
                    left = probe.left.getSimpleString()
                if probe.right.getSimpleString() == '-':
                    right = '0'
                else:
                    right = probe.right.getSimpleString()
                string += ("(%s,%s)" % (left, right))   
                probe = probe.next
                index += 1
                throwBeat = False
            if siteswap.isSymmetric():
                string += "*"   
            return string      

        else:
            probe = siteswap
            index = 0

            # point to first non-null beat
            while True: 
                if probe.left.throw != None or probe.right.throw != None:
                    break
                probe = probe.next

            if siteswap.isSymmetric():
                length = len(siteswap) // 2
            else:
                length = len(siteswap)

            while index < length:
                if len(probe.left) == 0 and len(probe.right) == 0:
                    isNull = True
                else:
                    isNull = False

                if len(probe.next.left) == 0 and len(probe.next.right) == 0:
                    nextIsNull = True
                else:
                    nextIsNull = False

                if probe.left.getSimpleString() == '-':
                    left = '0'
                else:
                    left = probe.left.getSimpleString()
                if probe.right.getSimpleString() == '-':
                    right = '0'
                else:
                    right = probe.right.getSimpleString()
                if nextIsNull:    
                    string += ("(%s,%s)" % (left, right))
                    index += 1
                    probe = probe.next
                else:
                    string += ("(%s,%s)!" % (left, right))
                index += 1
                probe = probe.next
            if siteswap.isSymmetric():
                string += "*"


            return string                

    def getVanillaStateString(self, siteswap = 0):
        if siteswap == 0:
            siteswap = self.siteswap


        if not siteswap.isVanilla():
            return "attempted to get vanilla state string when not vanilla"
        string = ""
        index = 0
        stateProbe = siteswap.state

        while index < len(siteswap.state) and stateProbe != None:
            if stateProbe.right == 0 and stateProbe.left == 0:
                string += '0'
            elif stateProbe.right != 0:
                string += str(stateProbe.right)
            else:
                string += str(stateProbe.left)    
            index += 1
            stateProbe = stateProbe.next

        return string

    def printSiteswap(self): 
        if self.siteswap.isValid() and not self.siteswap.isEmpty():
            self.siteswap.setIndices()
            print("\nValid %d-prop siteswap" % self.siteswap.getNumberProps())
            print("Indices:       " + self.getIndexStr())
            print("Siteswap:      " + str(self.siteswap))
            print("Rethrow line:  " + self.getRethrowStr())
            print()

        elif not self.siteswap.isEmpty(): 
            self.siteswap.setIndices()
            print("\nInvalid siteswap")
            print("Indices:       " + self.getIndexStr())
            print("Siteswap:      " + str(self.siteswap))
            print("Rethrow lines: " + self.getRethrowStr())
            print("               " + self.getInvalidRethrowStr())
            if self.siteswap.rethrowsNotShown:
                print(self.siteswap.rethrowsNotShownStr)
                print()
            else:
                print()
        else:
            print("\nSiteswap empty\n")

    def getRethrowStr(self):
        """Returns a string representation of the structure's rethrow values in MHN format"""
        string = ""
        i = 0
        probe = self.siteswap
        for node in self.siteswap:
            string += ("(%s,%s)" % (node.left.rethrowStr(), node.right.rethrowStr()))
        return string

    def getInvalidRethrowStr(self):
        """Returns a string representation of the structure's rethrow values in MHN format"""
        string = ""
        i = 0
        probe = self.siteswap
        for node in self.siteswap:
            string += ("(%s,%s)" % (node.left.invalidRethrowStr(), node.right.invalidRethrowStr()))
        return string

    def getIndexStr(self): 
        string = ""
        tempString = ""
        width = 0
        index = 0

        for node in self.siteswap:
            tempString = ("%s,%s" % (str(node.left), str(node.right)))
            width = len(tempString)
            string += "({:^{}})".format(str(index), width)
            index += 1

        return string
        