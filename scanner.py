"""
***************************************************************************
Filename:      scanner.py

Author:        David Mackie

Date:          2019.11.04

Modifications: 2019.11.04

Description:   This module defines a class scanner. Objects of this type
               receive a source string and iterate through it until reaching
               the end. For each scanned character, it prepares a Token 
               object with it to present to caller as needed. 
***************************************************************************
"""

from tokens import Token

class Scanner(object):

    EOP = ';'        # end-of-pattern
    TAB = '\t'       # tab

    def __init__(self, sourceStr):
        self._sourceStr = sourceStr
        self._getFirstToken()

    def hasNext(self):
        """Returns True if there is a character ready to be tokenized that isn't EOP"""

        return self._currentToken.getType() != Token.EOP

    def get(self):
        """Returns the current token. Does not scan next character"""

        return self._currentToken

    def next(self):
        """Returns the current token and scans the next character"""

        temp = self._currentToken
        self._getNextToken()
        return temp

    def getNextNext(self):
        """Returns the next token. Does not scan any characters or alter state"""

        self._skipWhiteSpace()
        if self._currentChar.isdigit():
            return Token(int(self._currentChar))
        elif self._currentChar == Scanner.EOP:
            return Token(';')
        else:
            return Token(self._currentChar)

    def stringUpToCurrentToken(self):
        """Returns string up until index"""

        return self._sourceStr[0:self._index]

    def _getFirstToken(self):
        """
        Initializes self._index, self._currentChar, and
        self._currentToken
        """
        self._index = 0
        self._currentChar = self._sourceStr[0]
        self._getNextToken()

    def _getNextToken(self):
        """Sets current character to current token and scans next character"""

        self._skipWhiteSpace()  # skip spaces and tabs

        # Set current character to current token - if digit, pass as integer
        if self._currentChar.isdigit():  
            self._currentToken = Token(int(self._currentChar))
            self._nextChar()
        elif self._currentChar == '\n':
            self._currentToken = Token(';')
        elif self._currentChar == Scanner.EOP:
            self._currentToken = Token(';')
        else:
            self._currentToken = Token(self._currentChar)
            self._nextChar()

    def _nextChar(self):
        """Scans next character of sourceStr while watching for EOP"""

        if self._index >= len(self._sourceStr) - 1:
            self._currentChar = Scanner.EOP

        else:
            self._index += 1
            self._currentChar = self._sourceStr[self._index]
    
    def _skipWhiteSpace(self):
        """Skips past white spaces in sourceStr"""
        
        while self._currentChar in (' ', Scanner.TAB):
            self._nextChar()



    # expand on this later when adding support for hexadecimal
    '''
    def _getInteger(self):
        num = 0
        while True:
            num = num * 10 + int(self._currentChar)
            self._nextChar()
            if not self._currentChar.isdigit():
                break
        return num
    '''

def main():
    # A simple tester program
    while True:
        sourceStr = input("Enter an expression: ")
        if sourceStr == "": break
        scanner = Scanner(sourceStr)
        token = scanner.get()
        while token.getType() != Token.EOP:
            print(token)
            scanner.next()
            token = scanner.get()

if __name__ == '__main__': 
    main()

