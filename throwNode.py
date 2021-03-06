"""
***************************************************************************
Filename:      throwNode.py

Author:        David Mackie

Date:          2019.11.04

Modifications: 2019.11.04

Description:   This module defines a class ThrowNode. This represents a 
               single throw made at a site, which may consist of more than
               one prop at once (multiplex). Objects of this class are intended
               to be built into null-terminated singly linked structures.
***************************************************************************
"""
from copy import deepcopy

class ThrowNode(object):
    # Add throw sort method (largest to smallest)
    def __init__(self, throw = None, throwX = False, next = None):
        """Instantiates a Node with a default next link of None and no throw value."""
        self.throw = throw              # siteswap value
        self.throwX = throwX            # True if ss value X'd
        self.next = next                # Points to multiplexed throw if any

        # IT MIGHT BE BETTER TO HAVE A SEPARATE CLASS TO DEAL WITH VALIDATION
        # Values for checking (validation) line
        self.rethrow = None        # Previous throw whose prop is rethrown at this site 
        self.rethrowX = False      # X value for checking line throw

        self.invalidRethrow = None
        self.invalidRethrowX = False

        self.indexStr = None

    def addThrow(self, throw):
        """
        Append ThrowNode object to linked structure. (for multiplexes)
        Structure is null-terminated
        """
        # If empty, set first nodes values to that of term's
        if self.isEmpty():
            self.throw = throw.throw
            self.throwX = throw.throwX
            self.next = None
            return

        # If not empty, add term to end of structure (null-terminated)
        throw.next = None
        probe = self
        while probe.next != None:
            probe = probe.next
        probe.next = throw

    def insertThrow(self, throw, index):
        """
        Insert throw at given index relative to self (should point to head of throw structure)
        Clear rethrow values of siteswap before calling this 
        Only inserts one throw at a time (don't pass a linked structure)
        """
        # If empty, set first nodes values to that of term's
        if self.isEmpty() or (self.throw == 0 and self.throwX == False and self.next == None):
            self.throw = throw.throw
            self.throwX = throw.throwX
            self.next = None
            return

        elif index >= len(self) or index < 0: # check this condtion ~~~~~~~~~~~~~~~~~~~~
            self.addThrow(throw)
            return
        
        elif index == 0:
            temp = deepcopy(self)
            self.throw = throw.throw
            self.throwX = throw.throwX
            self.next = temp
            return
        
        else:
            # Point to specified index in throwNode structure
            probe = self
            while index != 0:
                laggingProbe = probe
                probe = probe.next
                index -= 1

            # Insert
            throw.next = probe
            laggingProbe.next = throw
            return

    def deleteThrow(self, index):
        """
        Deletes throw at given index relative to self (self should point to head of throw structure)
        Clear rethrow values of siteswap before calling this 
        """
        # If empty, set first nodes values to that of term's
        if self.isEmpty() or (self.throw == 0 and self.throwX == False and self.next == None) or self.next == None:
            self.throw = None
            self.throwX = False
            self.next = None
            return

        elif index >= (len(self) -1):
            probe = self
            while probe.next.next != None:
                probe = probe.next
            probe.next = None
            return

        
        elif index == 0:
            temp = deepcopy(self)
            self.throw = self.next.throw
            self.throwX = self.next.throwX
            self.next = temp.next.next
            return
        
        else:
            # Point to specified index in throwNode structure
            probe = self
            while index != 0:
                laggingProbe = probe
                probe = probe.next
                index -= 1

            # Insert
            laggingProbe.next = probe.next
            return

    def clearRethrowValues(self):
        """Resets rethrow and rethrowX to None and False for all nodes in this structure"""
        for node in self:
            node.rethrow = None
            node.rethrowX = False
            node.invalidRethrow = None
            node.invalidRethrowX = False
            node.indexStr = None

    def getRethrowHand(self, hand):
        """
        Returns the hand that this throw will be caught/rethrown with
        """

        even = self.isEven()

        if even and hand == 'r':
            reHand = 'r'
        elif even and hand == 'l':
            reHand = 'l'
        elif not even and hand == 'r':
            reHand = 'l'
        elif not even and hand == 'l':
            reHand = 'r'

        if self.throwX and reHand == 'r':
            return 'l'
        elif self.throwX and reHand == 'l':
            return 'r'
        else:
            return reHand

    def isEven(self):
        """Returns True if the value is even; otherwise, returns False"""

        if self.throw % 2 == 0:
            return True
        else:
            return False  

    def isNull(self):
        if self.throw == None or self.throw == 0:
            return True
        else: 
            return False

    def isEmpty(self):
        """
        Returns True if length of the structure is zero (null with no next value)
        """

        if len(self) == 0:
            return True
        else: return False

    def __len__(self):
        """Returns length of structure. Returns 0 if no throws and no next term"""
        
        length = 0

        if self.next == None and self.throw == None:
            return 0

        probe = self
        while probe.next != None:
            length += 1
            probe = probe.next
        return length + 1

    def getSimpleString(self):
        """Returns a string representation of the throw value. Supports multiplex notation"""
        string = ""
        i = 0

        for node in self:
            if node.throw == None:
                throw = '-'
            elif node.throw >= 10:
                throw = chr(node.throw + 87)    # display as hex chr if >= 10
            else: throw = str(node.throw)

            if node.throwX:
                throwX = 'x'
            else:
                throwX = ""

            if len(self) > 1 and i == 0:
                string += '['

            string += throw + throwX
            if (len(self) > 1 and i == len(self) - 1):
                string += ']'
            i += 1

        return string

    def __str__(self):
        """Returns a string representation of the throw value. Supports multiplex notation"""
        string = ""
        i = 0

        for node in self:
            if node.throw == None:
                throw = '-'
            elif node.throw >= 10:
                throw = chr(node.throw + 87)    # display as hex chr if >= 10
            else: throw = str(node.throw)

            if node.throwX:
                throwX = 'x'
            elif node.rethrowX == True:
                throwX = " "
            else:
                throwX = ""

            if len(self) > 1 and i == 0:
                string += '['

            string += throw + throwX
            if (len(self) > 1 and i == len(self) - 1):
                string += ']'
            i += 1

        return string

    def rethrowStr(self):
        """Returns string representation of the rethrow value used for checking line."""

        string = ""
        i = 0
        for node in self:
            if node.rethrow == None:
                rethrow = '-'
            elif node.rethrow >= 10:
                rethrow = chr(node.rethrow + 87)    # display as hex chr if >= 10
            else: rethrow = str(node.rethrow)

            if node.rethrowX:
                rethrowX = 'x'
            elif node.throwX:
                rethrowX = " "         # To better allign rethrow line with string(self)
            else:
                rethrowX = ""

            if len(self) > 1 and i == 0:
                string += '['

            string += rethrow + rethrowX
            if (len(self) > 1 and i == len(self) - 1):
                string += ']'
            i += 1

        return string

    def invalidRethrowStr(self):
        """Returns string representation of the rethrow value used for checking line."""

        string = ""
        i = 0
        for node in self:
            if node.invalidRethrow == None:
                rethrow = '-'
            elif node.invalidRethrow >= 10:
                rethrow = chr(node.invalidRethrow + 87)    # display as hex chr if >= 10
            else: rethrow = str(node.invalidRethrow)

            if node.invalidRethrowX:
                rethrowX = 'x'
            elif node.throwX:
                rethrowX = " "         # To better allign rethrow line with string(self)
            elif node.rethrowX:
                rethrowX = " "
            else:
                rethrowX = ""

            if len(self) > 1 and i == 0:
                string += '['

            string += rethrow + rethrowX
            if (len(self) > 1 and i == len(self) - 1):
                string += ']'
            i += 1

        return string

    def isEqual(self, other):
        if other == None:
            return False

        probe1 = self
        probe2 = other

        if probe1.isNull() and probe2.isNull():
            return True
        if len(probe1) != len(probe2):
            return False

        length = len(probe1)
        i = 0
        while i < length:
            if probe1.isNull() and probe2.isNull():
                pass
            elif ((probe1.throw == probe2.throw) and (probe1.throwX == probe2.throwX)):
                pass 
            else:
                return False
            probe1 = probe1.next
            probe2 = probe2.next
            i += 1
        return True

    def __iter__(self): 
        """"
        Returns iterable object

        Allows throw structures to be iterated through
        """

        self.probe = self
        return self
  
    def __next__(self):  
        """
        Dictates behavior of next() function on throwNode iterators
        """
        if self.probe == None:
            raise StopIteration 
        else: 
            temp = self.probe
            self.probe = self.probe.next
            return temp


def main():


    a = ThrowNode(6,True, 'l')
    a.addThrow(ThrowNode(2,False))
    a.addThrow(ThrowNode(5,True))
    a.addThrow(ThrowNode(5,True))
    a.addThrow(ThrowNode(7,False))
    print(a)
    print()
    count = 1
    for i in a:
        print("throw",i.throw)
        print("X:", i.throwX)
        #print("hand:",i.hand)
        #print("rethrowHand:",i.getRethrowHand())
        print()
        count += 1

if __name__ == '__main__': main()