"""
***************************************************************************
Filename:      parsers.py

Author:        David Mackie

Date:          2019.11.04

Modifications: 2019.11.04

Description:   This module defines a class Parser. Objects of this type
               implement the following ENBF grammar on sourceStr passed to
               its parse method: 

SITESWAP Extended Backus-Naur Form (EBNF) GRAMMAR:
pattern = [prefix]term[postfix] {" "} {[prefix]term[postfix]}
term = async | sync
async = digit | multiplex
sync = "(" {" "} (digit | multiplex) {" "} "," {" "} (digit | multiplex) ")"
prefix = 'r' | 'R' | 'l' | 'L'
postfix = 'x' | 'X' | '!' | '*'
digit = "-" | "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "a" | "b" | "c" | "d" 

               This class uses a scanner to obtain Token objects of each 
               character of sourceStr as needed. 
***************************************************************************
"""

from tokens import Token
from scanner import Scanner
from siteswap import Siteswap
from throwNode import ThrowNode

class Parser(object):

    def parse(self, sourceStr):
        """
        Begin parsing sourceStr. Returns Siteswap object and whether or not
        not siteswap is valid
        """
        self._completionMessage = "No errors"    # Message depending on success 
        self._parseSuccessful = True             # True until parse fails
        self._hand = "r"                         # Hand to make next throw
        self._scanner = Scanner(sourceStr)       # Construct scanner object
        self.siteswap = self._pattern()         # Parse sourceStr into circular linked list

        self._accept(self._scanner.get(), Token.EOP,
                     "symbol after end of expression")
 
        return self.siteswap

    def _pattern(self):
        """Builds Siteswap circular linked structure representing siteswap from sourceStr"""

        siteswap = Siteswap() 
        siteswap.delete()            # Attempt to fix a bug
        token = self._scanner.get()

        # Stop adding terms when end of pattern (EOP) reached in sourceStr
        while token.getType() != Token.EOP:
            # Add term to siteswap, then check for postfixes before repeating
            siteswap.addTerm(self._term())      

            token = self._scanner.get()

            if token.getType() == Token.EXCL:
                self._scanner.next()
                token = self._scanner.get()
            elif siteswap.isLastSync():
                siteswap.addTerm(Siteswap())

            
            if token.getType() == Token.STAR:
                siteswap.makeSymmetric()
                self._scanner.next()
                return siteswap

        return siteswap

    def _term(self):
        """
        Returns a siteswap term to be added to the pattern.
        """
        # Loop to support prefix modifiers (L and R)
        while True:
            token = self._scanner.get()

            # Synchronous throw
            if token.getType() == Token.L_PAR:
                return self._syncTerm()

            # Asynchronous throw
            elif token.getType() == Token.INT:
                return self._asyncTerm()

            # Asynchronous multiplex throw
            elif token.getType() == Token.L_BRAC:
                return self._multiplex(self._hand)

            # L/R prefixes found 
            elif token.getType() == Token.LEFT:
                self._hand = 'l'
                self._scanner.next()
                continue
            elif token.getType() == Token.RIGHT:
                self._hand = 'r'
                self._scanner.next()
                continue

            else:
                self._fatalError(token, "Unrecognized character")
                return None
 
    def _syncTerm(self):
        
        self._scanner.next()            # Scan past left parentheses
        token = self._scanner.get()     # Get integer

        # Get LH throw
        if token.getType() == Token.L_BRAC:
            leftThrow = self._multiplex('l', True)

        elif token.getType() == Token.INT:
            left = token.getValue()
            leftX = self._isX()             # Get X modifier if needed
            leftThrow = ThrowNode(left, leftX, None)
            self._scanner.next()            # Scan to comma
        elif token.getType() == Token.NULL:
            leftThrow = ThrowNode(None, False, None)
            self._scanner.next()
        else: self._fatalError(token, "Unrecognized character")
        

        if self._scanner.next().getType() != Token.COMMA:
            self._fatalError(token, "Missing comma in sync term.")

        token = self._scanner.get()

        # Get RH throw
        if token.getType() == Token.L_BRAC:

            rightThrow = self._multiplex('r', True)

        elif token.getType() == Token.INT:
            right = token.getValue()
            rightX = self._isX()             # Get X modifier if needed
            rightThrow = ThrowNode(right, rightX, None)
            self._scanner.next()            # Scan to right parentheses
        elif token.getType() == Token.NULL:
            rightThrow = ThrowNode(None, False, None)
            self._scanner.next()
        else: self._fatalError(token, "Unrecognized character")

        if self._scanner.next().getType() != Token.R_PAR:
            self._fatalError(token, "Missing right parentheses")

        return Siteswap(leftThrow, rightThrow, None)

    def _asyncTerm(self):
        """Returns Siteswap object for async term"""

        # Get integer
        token = self._scanner.get()

        # Get X modifier if needed
        addX = self._isX()

        self._scanner.next()

        # Switch hands after each async throw
        if self._hand == "r":
            self._switchHand()
            throw = ThrowNode(token.getValue(), addX, None)
            return Siteswap(ThrowNode(), throw, None)
        else:
            self._switchHand()
            throw = ThrowNode(token.getValue(), addX, None)
            return Siteswap(throw, ThrowNode(), None)

    def _multiplex(self, hand, returnThrow = False):
        """
        Returns Siteswap object for multiplex term or ThrowNode object for
        multiplex throw (depending on returnThrow)
        """
        
        self._scanner.next()            # Scan past left bracket
        throw = ThrowNode(None, False, None)

        while True:
            token = self._scanner.get()     # Get integer
            addX = self._isX()             # Get X modifier if needed

            # Validate value or exit loop
            if token.getType() == Token.INT:
                throw.addThrow(ThrowNode(token.getValue(), addX))
                self._scanner.next()
            elif token.getType() == Token.R_BRAC and throw.isEmpty():
                self._fatalError(token, "Empty square brackets")
            elif token.getType() == Token.R_BRAC:
                self._scanner.next()
                break
            else: self._fatalError(token, "Unrecognized character")

        # Return multiplex throw or multplex term with a given hand
        if returnThrow:
            return throw
        elif hand == 'l':
            self._switchHand()
            return Siteswap(left = throw, right = ThrowNode())
        else:
            self._switchHand()
            return Siteswap(left = ThrowNode(), right = throw)

    def _isX(self):
        """
        Checks whether the current scanner value has an X after it
        Returns True if value is X'd and scans past it.
        Otherwise, it returns False and does not scan further.
        """
        token = self._scanner.getNextNext()
        if token.getType() == Token.X:
            self._scanner.next()
            return True
        else: 
            return False

    def _switchHand(self):
        '''Switches the hand scheduled for the next throw'''
        if self._hand == 'r':
            self._hand = 'l'
        else: 
            self._hand = 'r'
        return

    def parseStatus(self): return self._completionMessage

    def _accept(self, token, expected, errorMessage):
        """True if scanner reached end of sourceStr; otherwise False"""

        if token.getType() != expected:
            self._fatalError(token, errorMessage)

    def _fatalError(self, token, errorMessage):
        """Prints current token value to terminal and raises exception"""

        self._parseSuccessful = False
        self._completionMessage = "Parsing error -- " + \
                                  errorMessage + \
                                  "\nExpression so far = " + \
                                  self._scanner.stringUpToCurrentToken() + \
                                  "\nCurrent character: " + self._scanner.get().getValue() 
        raise Exception(self._completionMessage)





