import re

class MSTD():
    def __init__(self, mstd = ""):
        self.mstd = mstd
    def set(self, mstd = ""):
        self.mstd = mstd
    def isValid(self):
        # use re to check if self.mstd string is in proper format
    def getCoords(self):
        if self.isValid():
            # loop through all groups matched by RE and piece together JLab hand coordinates string.
    def getStateCoord(self):
        # given a state (Uli, Rlo, Urow, etc.) get the JLab coordinate string

    def getDirection(self):
    # examines current/next states and determines the direction a throw is made (in basic 1D: fanning in, fanning out, column) 

    """

    elif re.match(r'swa?p?\s+([0-9][0-9]?)([rRlL])([0-9][0-9]?)\s+([0-9][0-9]?)([rRlL])([0-9][0-9]?)\s*', userString) != None:
        swapRE = re.search(r'swa?p?\s+([0-9][0-9]?)([rRlL])([0-9][0-9]?)\s+([0-9][0-9]?)([rRlL])([0-9][0-9]?)\s*', userString)
        term1 = int(swapRE.group(1))
        hand1 = swapRE.group(2).lower()
        throw1 = int(swapRE.group(3))
        term2 = int(swapRE.group(4))
        hand2 = swapRE.group(5).lower()
        throw2 = int(swapRE.group(6))
        if (not term1 < len(self.siteswap)
    """