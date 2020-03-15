from siteswap import Siteswap
from throwNode import ThrowNode

class StateNode(object):
    def __init__(self, left = None, right = None):
        self.next = None
        self.left = left
        self.right = right
        self.complete = False

    def appendNullNode(self):
        if self.isEmpty():
            self.left = 0
            self.right = 0
            return

        probe = self
        # Search for node at the last position
        while probe.next != None:
            probe = probe.next
        # Insert new node after last position
        probe.next = StateNode(0,0)

    def addToNode(self, value, hand, index = 0):
        if self.isEmpty():
            self.left = 0
            self.right = 0

        if value == None:
            value = 0

        probe = self 

        while index != 0:
            if probe.next == None:
                self.appendNullNode()
            probe = probe.next
            index -= 1

        if hand == 'l': 
            probe.left += value
        else: 
            probe.right += value

    def propCount(self):
        count = 0
        probe = self
        while probe != None:
            if probe.left != None:
                count += probe.left
            if probe.right != None:
                count += probe.right
            probe = probe.next

        return count

    def getNode(self, index = 0):
        """Returns the term at the given index relative to self"""
        probe = self
        while index != 0:
            probe = probe.next
            index -= 1
        return probe

    def fillInZeros(self):
        if self.isEmpty():
            self.left = 0
            self.right = 0
            return

        index = 0
        probe = self
        while index < len(self):
            if probe.left == None:
                probe.left = 0
            if probe.right == None:
                probe.right = 0
            probe = probe.next
            index += 1

    def isEmpty(self):
        if self.next == None and self.left == None and self.right == None:
            return True
        else:
            return False

    def __str__(self):
        string = ""
        if self.isEmpty():
            return "(0, 0)"

        self.fillInZeros()
        index = 0
        probe = self
        while index < len(self):
            string += "(" + str(probe.left) + ", " + str(probe.right) +")"
            probe = probe.next
            index += 1
        return string

    def __len__(self):
        probe = self
   
        if self.isEmpty(): return 0

        length = 0
        while probe.next != None:
            length += 1
            probe = probe.next
        return length + 1

def main():
    state = StateNode()
    state.appendNullNode()
    state.addToNode(2,'l', 2)
    state.addToNode(1,'r',1)
    state = state.next # error prone only if bad programming

    print(state)
if __name__ == '__main__' : main() 