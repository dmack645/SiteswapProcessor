"""
***************************************************************************
Filename:      tokens.py

Author:        David Mackie

Date:          2019.11.04

Modifications: 2019.11.04

Description:   This module defines a class Token. Objects of this class
               hold whatever object is passed to it, and, if recognized,
               assigns it a type. 
***************************************************************************
"""

class Token(object):

    UNKNOWN  = 0        # unknown
    EOP      = 1        # end-of-expression
    L_PAR    = 2        # left parenthesis      note: parentheses contain sync throws (LH,RH)
    R_PAR    = 3        # right parenthesis
    INT      = 4        # integer
    COMMA    = 5        # comma
    X        = 6        # value is x'd. Rethrowing site handedness swapped
    STAR     = 7        # asterisk "*": make pattern symmetric
    L_BRAC   = 8        # left square bracket "[" (brackets enclose multiplex throws)
    R_BRAC   = 9        # right square bracket "]"
    LEFT     = 10       # left prefix modifier ('L')
    RIGHT    = 11       # right prefix modifier ('R')
    EXCL     = 12       # skip implied null beat ('!')
    NULL     = 13       # null beat ('-')
    HEX      = 14
            

    def __init__(self, value):
        if type(value) == int:
            self._type = Token.INT
            self._value = value
        # If values 'a' - 'f' == 10 - 15 (like in hexadecimal)
        elif ord(value) in range (ord('a'), ord('g')):
            self._type = Token.INT
            self._value = ord(value) - 87 
        else:
            self._type = self._makeType(value)
            self._value = value

    def __str__(self):
        """Returns string representation of value"""
        return str(self._value)

    def getType(self):
        """Returns type of value as int"""
        return self._type
    
    def getValue(self):
        """Returns value object"""
        return self._value

    def _makeType(self, ch):
        """If recognized, assign value a type"""

        if   ch == ',': return Token.COMMA
        elif ch == '(': return Token.L_PAR
        elif ch == ')': return Token.R_PAR
        elif ch == ';': return Token.EOP
        elif ch == 'x': return Token.X
        elif ch == 'X': return Token.X
        elif ch == '*': return Token.STAR
        elif ch == '%': return Token.STAR
        elif ch == '[': return Token.L_BRAC
        elif ch == ']': return Token.R_BRAC
        elif ch == 'L': return Token.LEFT
        elif ch == 'l': return Token.LEFT
        elif ch == 'R': return Token.RIGHT
        elif ch == 'r': return Token.RIGHT
        elif ch == '!': return Token.EXCL
        elif ch == '-': return Token.NULL
        else:           return Token.UNKNOWN;


