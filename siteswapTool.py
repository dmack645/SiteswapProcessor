"""
***************************************************************************
Filename:      siteswapTool.py

Author:        David Mackie

Date:          2019.11.04

Modifications: 2019.11.04

Description:   This module defines a class SiteswapValidator. Objects of 
               this type can be used to prompt the user to input a siteswap
               string to the terminal with the run() method. The function 
               creates and calls a Parser object and receives a Siteswap
               circular linked structure that represents the siteswaps in 
               MHN notation. It then prints whether or not the siteswap 
               is valid, along with the MHN and checking line. 
***************************************************************************
""" 

from siteswapParser import Parser
from siteswap import Siteswap
from siteswapValidator import SiteswapValidator
from stateGenerator import StateGenerator
import os
import webbrowser
"""
TODO
ADD DELETE/INSERT/MOVE FEATURE FOR TXT FILES
CONVERT FROM MHN STRUCTURE TO STRING IN JLAB NOTATION 


Program can run .bat files to use command prompt. (echo off)
select state and generate possible transitions into/out of pattern (select period)

BUGS

"""

class SiteswapTool(object):
    def __init__(self):
        self.header = "\n********************************************************************************************"
        self.siteswap = Siteswap()          # Empty siteswap
        self.userString = ""
        self.validator = SiteswapValidator()

    def run(self):
        textDict = self.getTextFilesDict()
        if len(textDict) == 0:
            self.getUserInput()

        else:
            print(self.header)
            print("Text files found:")
            self.chooseSiteswap()
            self.getUserInput()

    def getUserInput(self):
        while True:
            print(self.header)
            self.userString = input("Enter siteswap or option: ")
            if self.userString == '': 
                break
            elif self.userString == 's':
                self.saveSiteswap()
            elif self.userString == 'l':
                self.chooseSiteswap()
            elif self.userString == 'sr' or self.userString == 'sl':
                self.shift(self.userString)
                self.siteswap.printSiteswap()
            
            elif self.userString == 'state':
                self.stateMachine = StateGenerator()
                self.stateMachine.generateStates(self.siteswap)

            elif self.userString == 'jlab':
                jLab = self.siteswap.getJlabString()
                url = "https://jugglinglab.org/anim?pattern=" + jLab
                #url += ";gravity=2500.0;bps=6.5"
                webbrowser.open_new_tab(url)
                print("Attempting to load Juggling Lab gif in default browser.")
                print(jLab)
            
            else:
                self.rawSiteswap = self.userString
                self.siteswap = self.parseString(self.userString)
                if self.siteswap.isVanilla() and len(self.siteswap) % 2 != 0: 
                    self.siteswap.makeSymmetric()
                self.validator.validate(self.siteswap)
                self.siteswap.printSiteswap()

    def chooseSiteswap(self):
        textDict = self.getTextFilesDict()
        self.printDict(textDict)
        print("\nEnter index of file to open or press enter to continue: ", end = '')

        # User inputs index option or continues
        while True:
            fileIndex = input()
            if fileIndex == '':
                return

            elif fileIndex.isdigit() and (int(fileIndex) - 1)  in range(len(textDict)):
                file = open(textDict[int(fileIndex)])
                print("\nSiteswaps in " + textDict[int(fileIndex)] + ":")
                siteswapDict = self.getSiteswapDict(file)
                self.printDict(siteswapDict)

                print("\nEnter index of siteswap to open or press enter to continue: ", end = '')
                while True:
                    siteswapIndex = input()
                    if siteswapIndex == '': 
                        file.close()
                        return
                    elif siteswapIndex.isdigit() and (int(siteswapIndex) - 1) in range(len(siteswapDict)):
                        self.rawSiteswap = siteswapDict[int(siteswapIndex)]
                        self.siteswap = self.parseString(siteswapDict[int(siteswapIndex)])
                        self.validator.validate(self.siteswap) # add param "raw = True"
                        self.siteswap.printSiteswap()
                        file.close()
                        return
                    else: 
                        print("Invalid input. Try again: ", end = '')

            else: print("Invalid input. Try again: ", end = '')     

    def parseString(self, string):
        tempSiteswap = Siteswap()
        parser = Parser()               # Create Parser object

        try:
            tempSiteswap = parser.parse(string)
            #siteswap.printSiteswap()
        except Exception as e:
            print("Error:")
            print(e)
            tempSiteswap.delete()
        return tempSiteswap

    def saveSiteswap(self):
        textDict = self.getTextFilesDict()
        if len(textDict) == 0:
            self.createNewFile()
        else:
            print("Text files found:")

            while True:
                self.printDict(textDict)
                print("\nEnter index of file to open or 'n' for new file: ", end = '')
                fileIndex = input()
                if fileIndex == '':
                    return
                elif fileIndex == 'n':
                    self.createNewFile()
                    break
                elif fileIndex.isdigit() and (int(fileIndex) - 1)  in range(len(textDict)):
                    file = open(textDict[int(fileIndex)], 'r')

                    print("\nSiteswaps in " + textDict[int(fileIndex)] + ":")
                    siteswapDict = self.getSiteswapDict(file)
                    self.printDict(siteswapDict)

                    file.close()
                    file = open(textDict[int(fileIndex)], 'a+')


                    while True:
                        yesno = input("\nWrite to this file? (y/n): ")
                        if yesno == "y" or "Y" or "":
                            file.write(str(self.rawSiteswap) + '\n')
                            file.close()
                            return
                        else:
                            file.close()
                            break
                else: print("Invalid input. Try again: ", end = '')

    def createNewFile(self):
        fileName = input("Enter new file name: ")
        try:
            file = open(fileName, "w") # "w" for 'write'. Creates file if not already there
            file.write(str(self.rawSiteswap) + '\n')
            file.close()
        except Exception as e:
            print("Error writing to file:")
            #print(e)

    def shift(self, direction):
        if self.siteswap.isEmpty() or len(self.siteswap) == 1:
            return
        elif direction == 'sl':
            self.siteswap = self.siteswap.next
            self.validator.validate(self.siteswap)
        else:
            self.siteswap = self.siteswap.getTerm(len(self.siteswap) - 1)
            self.validator.validate(self.siteswap)
        return

    def getSiteswapDict(self, file):
        siteswapList = list()
        for string in file:
            
            tempSiteswap = self.parseString(string)
            self.validator.validate(tempSiteswap)
            if tempSiteswap.valid and not tempSiteswap.isEmpty():
                siteswapList.append(string)

        if len(siteswapList) == 0:
            return(dict())
        else:
            return {i + 1 : siteswapList[i].rstrip() for i in range(0, len(siteswapList))}
    
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

    def printDict(self, dictionary):
        for index in dictionary:
            print(str(index) + ": " + str(dictionary[index]))




def main():
    generator = SiteswapTool()


    generator.run()

if __name__ == "__main__": main()
