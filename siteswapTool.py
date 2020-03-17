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
from terminalSize import get_terminal_size
from asciiArt import getArt

"""
TODO
ADD DELETE/INSERT/MOVE FEATURE FOR TXT FILES
CONVERT FROM MHN STRUCTURE TO STRING IN JLAB NOTATION 


Program can run .bat files to use command prompt. (echo off)
select state and generate possible transitions into/out of pattern (select period)

Fix parser to not allow 0 in multiplex throw(as first [012] or otherwise [12303])
strip user input of lagging whitespace
"""

class SiteswapTool(object):
    
    def __init__(self):
        self.width = get_terminal_size()[0]
        self.header = ""
        self.jugglingArt = 6
        self.rawSiteswap = ''

        for i in range(0, self.width -1):
            self.header += '*'

        if self.jugglingArt != 6:
            print(self.header + '\n' + '{:^{}}'.format("SITESWAP IS FUN!", self.width))
            print(self.header)
        else:
            print(self.header)
            print('{:^{}}'.format(getArt(self.jugglingArt), self.width) +'\n' + self.header)
        self.siteswap = Siteswap()          # Empty siteswap
        self.userString = ""
        self.validator = SiteswapValidator()

    def run(self):
        print("Enter \"i\" for command list and info.\n")
        self.getUserInput()

    def getUserInput(self):
        while True:
            self.userString = input("Enter siteswap or command: ")
            if self.userString == '': 
                break
            elif self.userString == 'i':
                self.printInfo()
            elif self.userString == 's':
                self.saveSiteswap()
            elif self.userString == 'l':
                self.chooseSiteswap()
            elif self.userString == 'p':
                self.siteswap.printSiteswap()
            elif self.userString == 'sr' or self.userString == 'sl':
                self.shift(self.userString)
                self.siteswap.printSiteswap()
            
            elif self.userString == 'states':
                stateMachine = StateGenerator()
                print()
                stateMachine.printStates(self.siteswap)
            elif self.userString == 'state':
                self.pickState()

            elif self.userString == 'a':
                jLab = self.siteswap.getJlabString()
                url = "https://jugglinglab.org/anim?pattern=" + jLab
                #url += ";gravity=2500.0;bps=6.5"
                webbrowser.open_new_tab(url)
                print("Attempting to load Juggling Lab gif in default browser.")
                print(jLab)
            elif self.userString == 'jlab':
                #print("Current pattern in Juggling Lab compatible siteswap notation: ")
                print(self.siteswap.getJlabString())
            else:
                tempSiteswap = self.parseString(self.userString)
                self.validator.validate(tempSiteswap)

                if tempSiteswap is self.siteswap:
                    print() # Parsing error
                else:
                    self.siteswap = tempSiteswap
                    self.rawSiteswap = self.userString
                    self.siteswap.printSiteswap()

            self.width = get_terminal_size()[0]
            self.header = ""

            for i in range(0, self.width -1):
                self.header += '*'
            print(self.header)

    def pickState(self):
        stateMachine = StateGenerator()
        stateMachine.printStates(self.siteswap, quiet = True)
        while(True):
            index = input("\nEnter index of state to view: ")
            if index == '':
                print()
                return
            elif not index.isdigit():
                print("\nInvalid input.")
                continue
            elif int(index) in range(0, len(self.siteswap)):
                temp = self.siteswap.getTerm(int(index))
                stateMachine.printStates(temp, quiet = True)
                string = ""
                if self.siteswap.isVanilla():
                    string = stateMachine.getVanillaStateString()
                else:
                    string = str(temp.state)

                print("\nSiteswap: "+ temp.getSimpleString())
                print("Current State: " + string)

            else:
                print("\nInvalid input.")

    def chooseSiteswap(self):
        textDict = self.getTextFilesDict()
        print("\nText files found:")
        self.printDict(textDict)
        print("\nEnter pattern index or Enter to go back: ", end = '')

        # User inputs index option or continues
        while True:
            fileIndex = input()
            if fileIndex == '':
                print()
                return

            elif fileIndex.isdigit() and (int(fileIndex) - 1)  in range(len(textDict)):
                file = open(textDict[int(fileIndex)])
                print("\nSiteswaps in " + textDict[int(fileIndex)] + ":")
                siteswapDict = self.getSiteswapDict(file)
                self.printDict(siteswapDict)


                while True:
                    print("\nEnter siteswap index or Enter to go back: ", end = '')
                    siteswapIndex = input()
                    if siteswapIndex == '': 
                        file.close()
                        print()
                        return
                    elif siteswapIndex.isdigit() and (int(siteswapIndex) - 1) in range(len(siteswapDict)):
                        self.rawSiteswap = siteswapDict[int(siteswapIndex)]
                        self.siteswap = self.parseString(siteswapDict[int(siteswapIndex)])
                        self.validator.validate(self.siteswap) # detect for vanilla in validator
                        self.siteswap.printSiteswap()
                        file.close()
                        return
                    else: 
                        print("\nInvalid input.")

            else: print("\nInvalid input.")     

    def parseString(self, string, quiet = False):
        tempSiteswap = Siteswap()
        parser = Parser()               # Create Parser object

        try:
            tempSiteswap = parser.parse(string)
            #siteswap.printSiteswap()
        except Exception as e:
            if quiet == False:
                print("Error:")
                print(e)
            tempSiteswap.delete()
            return self.siteswap
        return tempSiteswap

    def saveSiteswap(self):
        textDict = self.getTextFilesDict()
        if len(textDict) == 0:
            self.createNewFile()
        else:
            print("\nText files found:")
            self.printDict(textDict)

            while True:

                print('\nEnter file index or "n" for new file: ', end = '')
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
                        if yesno == "y" or yesno == "Y":
                            file.write(str(self.rawSiteswap) + '\n')
                            file.close()
                            print()
                            return
                        else:
                            file.close()
                            print()
                            return
                else: print("\nInvalid input.")

    def createNewFile(self):
        fileName = input("\nEnter new file name or press Enter: ")
        if fileName == "":
            print()
            return
        fileName += ".txt"
        try:
            file = open(fileName, "w") # "w" for 'write'. Creates file if not already there
            file.write(str(self.rawSiteswap) + '\n')
            file.close()
            print()
        except Exception as e:
            print("Error writing to file:")
            #print(e)
            print()

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
            try:
                tempSiteswap = self.parseString(string, quiet = True)
            except:
                tempSiteswap = Siteswap()
                continue
            self.validator.validate(tempSiteswap)
            if not tempSiteswap.isEmpty():
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
    
    def printInfo(self):
        info = """
COMMANDS:
's'      : save siteswap to text file (existing or new)
'l'      : load siteswap from text file
'jlab'   : display notation used for JugglingLab notation
'a'      : animate in default browser using Juggling Lab
'p'      : print siteswap
'sr'     : shift right and print
'sl'     : shift left and print
'states' : print all states
'state'  : select index of state to print

"!" suffix on input term removes next implicit null beat
"*" suffix on input pattern appends hands-exchanged repeat to pattern
"R"/"L" prefix on input throw specifies which hand makes this throws
    (reverts back to alternating hands afterwards if vanilla)

Parser accepts most valid Juggling Lab siteswap notation (solo only).
Parser assumes implicit null beat after each sync term if no "-" values present.
Parser attempts to fill structure exactly as written.

Validator checks and possibly corrects pattern.
If siteswap invalid, validator tries symmetric form before giving up.
    (This means you can either enter "(6x,4)" or "(6x,4)*")
Odd lengthed vanilla siteswaps are made symmetric before validation.

"""
        print(info)


def main():
    generator = SiteswapTool()
    generator.run()

if __name__ == "__main__": main()
