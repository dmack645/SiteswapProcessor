"""
***************************************************************************
Filename:      termNode.py

Author:        David Mackie

Date:          2019.11.04

Modifications: 2019.11.04

Description:   This module defines a class termNode. This represents the available
               sites at a given beat in time in a siteswap pattern, and is the 
               basic building block of siteswap notation. 
               Objects of this class are intended to be built into circular singly 
               linked structures (implements the circular rule of siteswap for free).
               This class contains the bulk of methods that can be applied to a pattern.
***************************************************************************
""" 
# Might be good to create a validator class or function
'''
getState fills in "state" class variable for each term in the pattern
'''
from throwNode import ThrowNode

class Siteswap(object):
    """
    Represents a siteswap (or MHN) term. 

    Forms circular singly linked structure.
    """
    showInvalidFirstPass = False
    showIndexLine = True

    def __init__(self, left = ThrowNode(), right = ThrowNode(), next = None):
        """
        Instantiates a Node with a default next of None.
        """

        self.left = left
        self.right = right
        self.next = next
        self.valid = True
        self.errorString = ""
        self.symmetric = False
        self.modified = False

        self.rethrowsNotShown = False
        self.rethrowsNotShownStr = ""

        self.index = None
        self.state = None

    def addTerm(self, term):
        """
        Add a term to the end of the structure.
        This is the same as inserting a throwNode one link behind self
        """

        if self.isEmpty():
            self.left = term.left
            self.right = term.right
            self.next = self
            return

        term.next = self
        probe = self
        # Search for node at the last position
        while probe.next != self:
            probe = probe.next
        # Insert new node after last position
        probe.next = term

    def getTerm(self, index = 0):
        """Returns the term at the given index relative to self"""
        probe = self
        while index != 0:
            probe = probe.next    
            index -= 1
        return probe

    def getIndex(self, term):
        """Returns the index of the term relative to self (self has index = 0"""
        index = 0
        length = len(self)
        probe = self

        while index < length:
            if probe is term:
                return probe.index
            probe = probe.next
        return -1

    def setIndices(self):
        """Sets Siteswap self.index and ThrowNode self.index fields for the sitewap relative to self"""
        index = 0
        length = len(self)
        probe = self

        # Check for empty siteswap
        if probe.isEmpty():
            probe.index = 0
            return


        while index < length:
            probe.index = index   # Set Siteswap index

            # Set probe.left index
            throw = probe.left
            while throw != None:
                throw.indexStr = str(index) + 'l'
                throw = throw.next

            # Set probe.right index
            throw = probe.right
            while throw != None:
                throw.indexStr = str(index) + 'r'
                throw = throw.next

            probe = probe.next
            index += 1 

    def setValidity(self, validity):
        index = 0
        length = len(self)
        probe = self

        # Check for empty siteswap
        if probe.isEmpty():
            probe.valid = True 
            return


        while index < length:
            probe.valid = validity   # Set validity
            probe = probe.next 
            index += 1

    def isRethrowFull(self, hand):
        if hand == 'l':
            probe = self.left
        else: 
            probe = self.right

        while probe != None:
            if probe.rethrow == None:
                return False
            probe = probe.next
        return True

    def isValid(self):
        for term in self:
            for throw in term.right:
                if throw.throw == None and throw.rethrow != None:
                    return False
                if throw.throw != None and throw.rethrow == None:
                    return False
            for throw in term.left:
                if throw.throw == None and throw.rethrow != None:
                    return False
                if throw.throw != None and throw.rethrow == None:
                    return False
        return True

    def isSymmetric(self):
        # Eventually add support for odd period patterns (for weird MHN patterns with symmetric middle term)
        length = len(self)

        if length % 2 != 0:
            return False

        outerIndex = 0

        laggingProbe = self
        leadingProbe = self.getTerm(length//2) # Points to first term in second half

        # Search for node at the last position
        # leadingProbe points to end, laggingProbe follows from beginning
        while outerIndex < (length//2):
            if (not laggingProbe.left.isEqual(leadingProbe.right) or (not laggingProbe.right.isEqual(leadingProbe.left))):
                innerIndex = 0
                while innerIndex < length:
                    leadingProbe.symmetric = False
                    leadingProbe = leadingProbe.next
                    innerIndex += 1
                return False

            else:
                leadingProbe.symmetric = True
                laggingProbe.symmetric = True
                leadingProbe = leadingProbe.next
                laggingProbe = laggingProbe.next
                outerIndex += 1
        return True

    def makeSymmetric(self):
        """
        Adds on a second half that mirrors the first half (hands switched)

        Precondition: self must point to the header node of a structure
        """
        self.clearRethrowValues()
        length = len(self)
        i = 0

        probe = self

        # Search for node at the last position
        # leadingProbe points to end, laggingProbe follows from beginning
        while i < length:
            term = Siteswap(ThrowNode(), ThrowNode(), next = self) # don't think I need to point next to pattern
            term.symmetric = True
            # Add throws from laggingProbe to leadingProbe (swap handedness)
            for node in probe.left:
                right = ThrowNode(node.throw, node.throwX, None)
                term.right.addThrow(right)

            for node in probe.right:
                left = ThrowNode(node.throw, node.throwX, None)
                term.left.addThrow(left)
            self.addTerm(term)
            probe.symmetric = True
            probe = probe.next
            i += 1

    def makeAsymmetric(self):
        """
        Throws out second half of pattern.

        Precondition: length of structure must be even
        """
        self.clearRethrowValues()
        if len(self) % 2 == 0 and len(self) >= 2:
            i = int((len(self) / 2) - 1)  # index of last term in first half
            probe = self

            # Find last term in first half of structure
            for term in range (0, i):
                probe.symmetric = False
                probe = probe.next

            # Link this probe to self, removing second half from structure
            probe.next = self

    def getNumberProps(self):
        """Returns the number of props being juggled"""
        if len(self) != 0:
            # Get sum of all throw values in pattern
            sumOfThrows = 0
            for term in self:
                for node in term.left:
                    if node.throw != None:
                        sumOfThrows += node.throw
                for node in term.right:
                    if node.throw != None:
                        sumOfThrows += node.throw

            # Divide by length to get average, which is number of props
            numProps = sumOfThrows/len(self)
            return numProps
        else: return 0

    def clearRethrowValues(self):
        """
        Traverses structure and sets self.rightCheck and self.leftCheck to None 
        for all terms.
        """

        for node in self:
            node.left.clearRethrowValues()
            node.right.clearRethrowValues()
            node.rethrowsNotShown = False
            node.rethrowsNotShownStr = ""

    def isLastSync(self):
        """
        Returns True if the last term relative to self is synchronous
        """

        if self.isEmpty():
            return False
        probe = self
        # Search for node at the last position
        while probe.next != self:
            probe = probe.next

        # Insert new node after node at position index - 1
        # or last position
        if not probe.left.isEmpty() and not probe.right.isEmpty():
            return True
        else:
            return False

    def getVanillaFirstHand(self):
        index = 0
        length = len(self)
        probe = self

        while index < length:
            if probe.left.isNull() and not probe.right.isNull():
                return 'r'
            elif probe.right.isNull() and not probe.left.isNull():
                return 'l'
            probe = probe.next 
            index += 1
        return 'r'

    def getVanillaFirstIndex(self):
        index = 0
        length = len(self)
        probe = self

        while index < length:
            if probe.left.isNull() and probe.right.isNull():
                probe = probe.next 
                index += 1
            else:
                return index


        return 0

    def isVanilla(self):
        """Returns True if async vanilla siteswap"""
        # Check for empty siteswap
        if self.isEmpty(): return True

        hand = None

        index = 0
        length = len(self)
        probe = self
        while index < length:
            if probe.left.isNull() and not probe.right.isNull():
                if hand == 'r':
                    return False
                else:
                    hand = 'r'
            elif probe.right.isNull() and not probe.left.isNull():
                if hand == 'l':
                    return False
                else:
                    hand = 'l'
            elif len(probe.left) >= 1 and len(probe.right) >= 1:
                return False
            probe = probe.next 
            index += 1

        return True

    def isInvalidFull(self, hand):
        if hand == 'l':
            probe = self.left
        else: 
            probe = self.right

        while probe != None:
            if probe.invalidRethrow == None:
                return False
            probe = probe.next
        return True

    def isEmpty(self):
        """
        Returns True if no throws made this term and there's no next term.
        Otherwise, return False
        """

        if self.left.isEmpty() and self.right.isEmpty() and self.next == None:
            return True
        else: return False

    def delete(self):
        """Deletes content of structure - only one empty node remains"""
        self.next = None
        self.left = ThrowNode()
        self.right = ThrowNode()

    def getRethrowStr(self):
        """Returns a string representation of the structure's rethrow values in MHN format"""
        string = ""
        i = 0
        probe = self
        for node in self:
            string += ("(%s,%s)" % (node.left.rethrowStr(), node.right.rethrowStr()))
        return string

    def getInvalidRethrowStr(self):
        """Returns a string representation of the structure's rethrow values in MHN format"""
        string = ""
        i = 0
        probe = self
        for node in self:
            string += ("(%s,%s)" % (node.left.invalidRethrowStr(), node.right.invalidRethrowStr()))
        return string

    def getIndexStr(self):
        string = ""
        tempString = ""
        width = 0
        for node in self:
            tempString = ("%s,%s" % (str(node.left), str(node.right)))
            width = len(tempString)
            string += "({:^{}})".format(str(node.index), width)
        return string

    def printSiteswap(self):
            if self.valid and not self.isEmpty():
                self.setIndices()
                print("\nValid %d-prop siteswap" % self.getNumberProps())
                print("Indices:       " + self.getIndexStr())
                print("Siteswap:      " + str(self))
                print("Rethrow line:  " + self.getRethrowStr())
                print()

            elif not self.isEmpty(): 
                self.setIndices()
                print("\nInvalid siteswap")
                print("Indices:       " + self.getIndexStr())
                print("Siteswap:      " + str(self))
                print("Rethrow lines: " + self.getRethrowStr())
                print("               " + self.getInvalidRethrowStr())
                if self.rethrowsNotShown:
                    print(self.rethrowsNotShownStr)
                    print()
                else:
                    print()
            else:
                print("Siteswap empty")

    def __len__(self):
        """Returns the number of terms in the structure"""
        probe = self
        length = 0
        if self.isEmpty():
            return 0

        while probe.next != self:
            length += 1
            probe = probe.next
        return length + 1

    def getSimpleString(self):
        """Returns a string representation of the structure in MHN format"""


        if self.isVanilla():
            return self.getJlabString()
        else:
            string = ""
            i = 0
            probe = self
            for node in self:
                string += ("(%s,%s)" % (node.left.getSimpleString(), node.right.getSimpleString()))
            return string

    def __str__(self):
        """Returns a string representation of the structure in MHN format"""

        string = ""
        i = 0
        probe = self

        for node in self:
            string += ("(%s,%s)" % (str(node.left), str(node.right)))
        return string

    def getJlabString(self):
        """Returns a string representation of the structure in JLAB format"""
        string = ""
        index = 0
        probe = self

        if not self.isVanilla():
            for node in self:   # REVISE THIS TO USE PROBE~~~~~~~~~~~~
                if str(node.left) == '-':
                    left = '0'
                else:
                    left = str(node.left)
                if str(node.right) == '-':
                    right = '0'
                else:
                    right = str(node.right)
                string += ("(%s,%s)!" % (left, right))
            return string

        else:   # Vanilla
            hand = self.getVanillaFirstHand()
            firstIndex = self.getVanillaFirstIndex()

            # Point to first index that isn't zero
            while firstIndex != 0:
                probe = probe.next
                firstIndex -= 1

            if self.symmetric:
                patternLength = len(self) // 2
            else:
                patternLength = len(self)

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

    def __iter__(self): 
        """"Returns iterable object. Allows for 'for' loops and iter()"""
        self.probe = self
        self.i = 0
        return self
  
    def __next__(self):  
        """Behavior of next() on iter(self)"""
        if self.i >= len(self):
            raise StopIteration 
        else: 
            temp = self.probe
            self.probe = self.probe.next
            self.i += 1
            return temp  



    '''
    # TO BE USED LATER
    def addX(self, left = False, right = False):
        """
        Adds 'x' modifiers to the last term
        I'll use this later on when I add siteswap transforms
        """
        probe = self
        # Search for node at the last position
        while probe.next != self:
            probe = probe.next

        probe.leftX = left
        probe.rightX = right
    '''