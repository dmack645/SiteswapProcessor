from siteswap import Siteswap
from throwNode import ThrowNode

class SiteswapValidator(object):
    def __init__(self):
        self.pattern = Siteswap()

    def validate(self, pattern):
        self.pattern = pattern


        self.fillRethrowLine() 

        if self.isValid():
            self.pattern.setValidity(True)
        else:
            self.tryAgainSymmetric()

        return self.pattern.valid

    def isValid(self):
        for term in self.pattern:
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

    def fillRethrowLine(self):
        """Fill in the rethrow line for validation"""
        self.pattern.clearRethrowValues()  # Temporary fix for a bug I can't seem to fix
                                   # Rethrow values from previous parser.run() calls 
                                   # were remaining in rethrow fields

        # Outer loop traverses structure
        for outerProbe in self.pattern:
            # Left hand throwing site
            if not outerProbe.left.isEmpty(): 
                # Find/fill rethrow site for each throw at this site (>1 if multiplex)

                node = outerProbe.left
                while node != None:
                    # Set up inner probe, get value, counter, and rethrowHand.
                    value = node.throw
                    s = value
                    innerProbe = outerProbe
                    rethrowHand = node.getRethrowHand('l')  # Hand this value is rethrown with
                    addX = node.throwX

                    # Find rethrowing site for this throw
                    while s > 0:
                        innerProbe = innerProbe.next
                        s -= 1

                    # Check rethrow site for collisions and contradictions
                    # Right hand rethrowing site   
                    if rethrowHand == 'r':
                        self.insertRethrowAndCheck(value, addX, innerProbe, innerProbe.right, 'r')

                    # Left hand rethrowing site
                    else: 
                        self.insertRethrowAndCheck(value, addX, innerProbe, innerProbe.left, 'l')
                        # Check each throw in the rethrow site
                    node = node.next

            # Right hand throwing site               
            if not outerProbe.right.isEmpty(): 
                # Find/fill rethrow site for each throw at this site (>1 if multiplex)
                node = outerProbe.right
                while node != None:
                    # Set up inner probe, get value, counter, and rethrowHand.
                    value = node.throw
                    s = value
                    innerProbe = outerProbe
                    rethrowHand = node.getRethrowHand('r')  # Hand this value is rethrown with
                    addX = node.throwX


                    # Find rethrowing site for this throw
                    while s > 0:
                        innerProbe = innerProbe.next
                        s -= 1

                    # Check rethrow site for collisions and contradictions
                    # Right hand rethrowing site 
                    if rethrowHand == 'r':
                        self.insertRethrowAndCheck(value, addX, innerProbe, innerProbe.right, 'r')

                    # Left hand rethrowing site
                    else:   
                        self.insertRethrowAndCheck(value, addX, innerProbe, innerProbe.left, 'l')
                    node = node.next
        
    def insertRethrowAndCheck(self, value, addX, term, throw, hand):
        """Insert value/addX in rethrow/rethrowX fields of node if possible"""
        self.pattern.setIndices()
        length = len(throw)

        while throw != None:
            # Value in MHN and not in rethrow (Valid)
            if throw.throw != None and throw.rethrow == None:
                throw.rethrow = value
                throw.rethrowX = addX
                break

            # Value in MHN, value in rethrow, value not in invalid rethrow, rethrow full
            elif throw.throw != None and throw.rethrow != None and throw.invalidRethrow == None and term.isRethrowFull(hand):
                throw.invalidRethrow = value
                throw.invalidRethrowX = addX
                break

            # Value in MHN, value in rethrow, value not in invalid rethrow, rethrow not full
            elif throw.throw != None and throw.rethrow != None and throw.invalidRethrow == None and not term.isRethrowFull(hand):
                throw = throw.next
                continue

            # Value in MHN, value in rethrow, value in invalid rethrow, rethrow full, invalid full
            elif throw.throw != None and throw.rethrow != None and throw.invalidRethrow != None and term.isRethrowFull(hand) and term.isInvalidFull(hand):
                if self.pattern.rethrowsNotShown == False:
                    self.pattern.rethrowsNotShownStr += "Some invalid throws not shown: "
                    self.pattern.rethrowsNotShown = True
                if addX:
                    self.pattern.rethrowsNotShownStr += throw.indexStr + ":" + str(value) + "x" + "   "
                else:
                    self.pattern.rethrowsNotShownStr += throw.indexStr + ":" + str(value) + "   "
                break

            # Value in MHN, value in rethrow, value in invalid rethrow, rethrow full, invalid not full
            elif throw.throw != None and throw.rethrow != None and throw.invalidRethrow != None and term.isRethrowFull(hand) and not term.isInvalidFull(hand):
                throw = throw.next
                continue



            # Value not in MHN, value not in rethrow
            elif throw.throw == None and throw.rethrow == None:
                throw.rethrow = value
                throw.rethrowX = addX
                break

            # Value not in MHN, value in rethrow, value not in invalid rethrow, rethrow full
            elif throw.throw == None and throw.rethrow != None and throw.invalidRethrow == None:
                throw.invalidRethrow = value
                throw.invalidRethrowX = addX
                break


            # Value not in MHN, value in rethrow, value in invalid rethrow, rethrow full
            elif throw.throw == None and throw.rethrow != None and throw.invalidRethrow != None:
                if self.pattern.rethrowsNotShown == False:
                    self.pattern.rethrowsNotShownStr += "Some invalid throws not shown: "
                    self.pattern.rethrowsNotShown = True
                if addX:
                    self.pattern.rethrowsNotShownStr += throw.indexStr + ":" + str(value) + "x" + "   "
                else:
                    self.pattern.rethrowsNotShownStr += throw.indexStr + ":" + str(value) + "   "
                break
            throw = throw.next
    
    def isRethrowFull(self, hand):
        if hand == 'l':
            probe = self.pattern.left
        else: 
            probe = self.pattern.right

        while probe != None:
            if probe.rethrow == None:
                return False
            probe = probe.next
        return True

    def isInvalidFull(self, hand):
        if hand == 'l':
            probe = self.pattern.left
        else: 
            probe = self.pattern.right

        while probe != None:
            if probe.invalidRethrow == None:
                return False
            probe = probe.next
        return True

    def tryAgainSymmetric(self):
        """
        If validation fails on the first pass, make the siteswap symmetric and try again.
        """
        # Option to print invalid siteswap/rethrow lines before trying symmetric version
        if Siteswap.showInvalidFirstPass:
            self.pattern.setValidity(False)
            self.pattern.printSiteswap()
            print("Let's try making it symmetric:")
        self.pattern.makeSymmetric()
        self.fillRethrowLine()

        if self.isValid():
            self.pattern.setValidity(True)
        else:
            self.pattern.setValidity(False)
            if Siteswap.showInvalidFirstPass: self.pattern.printSiteswap()
            self.pattern.makeAsymmetric()
            self.fillRethrowLine()


