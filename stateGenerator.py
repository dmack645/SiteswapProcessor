from siteswap import Siteswap
from throwNode import ThrowNode
from siteswapValidator import SiteswapValidator
from stateNode import StateNode

class StateGenerator(object):
    def __init__(self):
        self.validator = SiteswapValidator()

    def generateStates(self, pattern):
        self.pattern = pattern
        self.state = StateNode()
        self.validator.validate(self.pattern)

        if not self.validator.isValid():
            print("Siteswap invalid - cannot generate states")

        if self.pattern.isEmpty():
            self.pattern.state = self.state
            return

        patternProbe = self.pattern
        index = 0 

        # Fill in first node according to number of throws to come from left/right hand
        while self.state.propCount() < self.pattern.getNumberProps():
            self.loadFirstNode(patternProbe)
            self.throwThis(patternProbe)
            patternProbe = patternProbe.next
            index += 1
            if index == len(self.pattern):
                index = 0  
            #print("balls: " + str(self.state.propCount()))
        
        # Rotate back to beginning of original pattern
        while index != 0:
            self.throwThis(patternProbe)
            patternProbe = patternProbe.next
            index += 1
            if index == len(self.pattern):
                break
        
        index = 0
        print("Pattern: " + str(self.pattern))
        print()
        print("States:")

        while index < len(self.pattern):
            print(self.state, end = '  --> ')
            print("(%s,%s)" % (str(self.pattern.left), str(self.pattern.right)))
            self.throwThis(self.pattern)
            self.pattern = self.pattern.next
            index +=1
            print()


    def throwThis(self, term):
        index = 0
        for throw in term.left:
            if throw.throw == None: continue
            hand = throw.getRethrowHand('l')
            self.state.addToNode(1, hand, index = throw.throw)
        for throw in term.right:
            if throw.throw == None: continue
            hand = throw.getRethrowHand('r')
            self.state.addToNode(1, hand, index = throw.throw)
        if self.state.next == None:
            #print("error: next state during shift step is None")
            self.state.left = 0
            self.state.right = 0
        else:
            self.state = self.state.next
                


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


                                                                                           
