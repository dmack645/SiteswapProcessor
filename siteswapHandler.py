from siteswapParser import Parser
from siteswap import Siteswap
from siteswapValidator import SiteswapValidator
from stateGenerator import StateGenerator
import os
import webbrowser

class SiteswapHandler(object):
    def __init__(self):
        self.siteswap = Siteswap()
        self.validator = SiteswapValidator()
        self.stateGenerator = StateGenerator()

    def parseString(self, string, quiet = True):
        tempSiteswap = Siteswap()
        parser = Parser()               

        try:
            tempSiteswap = parser.parse(string)
            #siteswap.printSiteswap()
        except Exception as e:
            if quiet == False:
                print("Error:")
                print(e)
            tempSiteswap.delete()
            return False 
        return tempSiteswap

    def validate(self, siteswap):
        return self.validator.validate(siteswap)

    def shift(self, siteswap, direction):
        if siteswap.isEmpty() or len(siteswap) == 1:
            return
        elif direction == 'sl':
            return siteswap.next
            self.validator.validate(siteswap)
        else:
            return siteswap.getTerm(len(siteswap) - 1)
        return
           
    def getTextFilesDict(self):
        fileList = os.listdir()
        textList = list()
        for fileName in fileList:
            if '.txt' in fileName:
                file = open(fileName)
                if len(self.getSiteswapDict(file)) != 0:
                    textList.append(fileName)
                file.close()

        if len(textList) == 0:
            return(dict())
        else:
            return {i + 1 : textList[i] for i in range(0, len(textList))}

    def getSiteswapDict(self, file):
        siteswapList = list()
        for string in file:
            if self.parseString(string) != False:
                if not self.parseString(string).isEmpty():
                    siteswapList.append(string)

        if len(siteswapList) == 0:
            return(dict())
        else:
            return {i + 1 : siteswapList[i].rstrip() for i in range(0, len(siteswapList))}

    def writeStrToFile(self, string, fileName):
        file = open(fileName, 'a+')
        file.write(string + '\n')
        file.close()

    def generateStates(self, siteswap):
        self.stateGenerator.generate(siteswap)