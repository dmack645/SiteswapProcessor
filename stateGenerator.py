from siteswap import Siteswap
from throwNode import ThrowNode
from siteswapValidator import SiteswapValidator
from stateNode import StateNode
from copy import deepcopy

class StateGenerator(object):
    def __init__(self):
        self.validator = SiteswapValidator()

    def generate(self, pattern):
        self.pattern = pattern
        self.state = StateNode()
        self.validator.validate(self.pattern)



        if self.pattern.isEmpty() or not self.pattern.isValid():
            return

        self.pattern = self.pattern
        self.fillStates()

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
        while True:
            self.throwThis()

            index += 1
            if index == len(self.pattern):
                break

        index = 0
        while index < len(self.pattern):
            self.pattern.state = deepcopy(self.state)
            self.throwThis()
            index += 1

        '''
        while True:
            self.throwThis()

            index += 1
            if index == len(self.pattern):
                break
        '''

        # Go through whole pattern and add deepcopy of state to each term

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








                                                                                           
