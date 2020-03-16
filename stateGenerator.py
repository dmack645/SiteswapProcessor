from siteswap import Siteswap
from throwNode import ThrowNode
from siteswapValidator import SiteswapValidator
from stateNode import StateNode
from copy import deepcopy

class StateGenerator(object):
    def __init__(self):
        self.validator = SiteswapValidator()

    def fillStates(self):
        index = 0 

        # Fill in first node according to number of throws to come from left/right hand
        while self.state.propCount() < self.pattern.getNumberProps():
            self.loadFirstNode(self.pattern)
            self.throwThis()
 
            index += 1 # Index keeps track of position in pattern
            if index == len(self.pattern):
                index = 0  
            #print("balls: " + str(self.state.propCount()))
        
        # Rotate back to beginning of original pattern
        while index != 0:
            self.throwThis()

            index += 1
            if index == len(self.pattern):
                break

    def printStates(self, pattern, quiet = False):
        self.pattern = pattern
        self.state = StateNode()
        self.validator.validate(self.pattern)

        if not self.validator.isValid():
            print("Siteswap invalid - cannot generate states")

        if self.pattern.isEmpty():
            self.pattern.state = self.state
            return

        self.pattern = self.pattern
        self.fillStates()

        
        #'{:10}'.format('test')
        if not quiet: 
            print("Siteswap: \n" + self.pattern.getSimpleString())
            print()
            print("States:")
            maxLength = self.getMaxStateLength()
            if self.pattern.isVanilla():
                hand = self.pattern.getVanillaFirstHand()
                foundValue = False
                index = 0
                while index < len(self.pattern):
                    stateString = self.getVanillaStateString()
                    #       string += "({:^{}})".format(str(node.index), width)
                    print('{:<{}}'.format(stateString, maxLength), end = '  --> ')
                    if hand == 'r':
                        print(self.pattern.right.getSimpleString())
                        if not self.pattern.right.isNull() and not foundValue:
                            foundValue = True
                        if foundValue:
                            hand = 'l'
                    else:
                        print(self.pattern.left.getSimpleString())
                        if not self.pattern.left.isNull() and not foundValue:
                            foundValue = True
                        if foundValue:
                            hand = 'r'

                    self.throwThis()

                    index +=1
                    print()

            else:
                maxLength *= 5

                index = 0
                while index < len(self.pattern):
                    print('{:<{}}'.format(str(self.state), maxLength), end = '  --> ')

                    print("(%s,%s)" % (self.pattern.left.getSimpleString(), self.pattern.right.getSimpleString()))
                    self.throwThis()
                    index +=1
                    print()
            


    def getVanillaStateString(self):
            if not self.pattern.isVanilla():
                return "attempted to get vanilla state string when not vanilla"
            string = ""
            index = 0
            stateProbe = self.state

            while index < len(self.state):
                # Test to see if self.state.throwThis() alters self.state
                # I'm pretty sure it must
                if stateProbe.right == 0 and stateProbe.left == 0:
                    string += '0'
                elif stateProbe.right != 0:
                    string += str(stateProbe.right)
                else:
                    string += str(stateProbe.left)    
                index += 1
                if stateProbe.next != None: stateProbe = stateProbe.next
            return string

    def throwThis(self):
        self.state
        for throw in self.pattern.left:
            if throw.throw == None: continue
            hand = throw.getRethrowHand('l')
            self.state.addToNode(1, hand, index = throw.throw)
        for throw in self.pattern.right:
            if throw.throw == None: continue
            hand = throw.getRethrowHand('r')
            self.state.addToNode(1, hand, index = throw.throw)
        if self.state.next == None:
            #print("error: next state during shift step is None")
            self.state.left = 0
            self.state.right = 0
        else:
            self.state = self.state.next
        self.pattern = self.pattern.next
                
    def loadFirstNode(self, term):
        if self.state.left == None:
            self.state.left = 0
        if self.state.right == None:
            self.state.right = 0
        if len(term.left) > self.state.left:
            if self.state.left > len(term.left):
                print("error loading first term(l)")
            self.state.left = len(term.left)
        if len(term.right) > self.state.right:
            if self.state.right > len(term.right):
                print("error loading first term(r)")
            self.state.right = len(term.right)

    def getMaxStateLength(self):
        """
        Returns the max state length (I think this is always largest SS value)
        """
        tempPattern = deepcopy(self.pattern)
        tempState = deepcopy(self.state)

        maxLength = 0
        index = 0

        # Find state length for each position in pattern
        while index < len(self.pattern): 
            maxLength = max(len(self.state), maxLength)
            self.throwThis()
            index += 1
        self.pattern = tempPattern
        self.state = tempState
        return maxLength






                                                                                           
