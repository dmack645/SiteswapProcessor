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
from stateGenerator import StateGenerator
import os
import webbrowser
from terminalSize import get_terminal_size
from asciiArt import getArt
from siteswapHandler import SiteswapHandler

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
    jugglingArt = 6 
    def __init__(self):
        self.rawSiteswap = ''
        self.printWelcome()

        self.siteswap = Siteswap()          # Empty siteswap

    def run(self):
        self.handler = SiteswapHandler()
        print("Enter \"i\" for command list and info.\n")
        userString = ''
        while True:
            userString = input("Enter siteswap or command: ").strip()
            if userString == '': 
                break
            elif userString == 'i':
                self.printInfo()
            elif userString == 'l':
                self.chooseSiteswap()
            elif userString == 's':
                self.saveSiteswap()
            elif userString == 'p':
                self.siteswap.printSiteswap()
            elif userString == 'sr' or userString == 'sl':
                self.siteswap = self.handler.shift(self.siteswap, userString)
                self.siteswap.printSiteswap()
            
            elif userString == 'states':
                self.printStates()

            elif userString == 'state':
                self.pickState()

            elif userString == 'a':
                jLab = self.siteswap.getJlabString()
                url = "https://jugglinglab.org/anim?pattern=" + jLab
                #url += ";gravity=2500.0;bps=6.5"
                webbrowser.open_new_tab(url)
                print("\nAttempting to load Juggling Lab gif in default browser.")
                print("Siteswap string: " + jLab + '\n')
            elif userString == 'jlab':
                #print("Current pattern in Juggling Lab compatible siteswap notation: ")
                print('\n' + self.siteswap.getJlabString() + '\n')
            else:
                if self.handler.parseString(userString, quiet = False) != False:
                    self.rawSiteswap = userString
                    self.siteswap = self.handler.parseString(userString, quiet = False)
                    self.handler.validate(self.siteswap)
                    self.siteswap.printSiteswap()
                else:
                    print()
            self.printHeader()
            print()

    def printStates(self):
        if not self.siteswap.isValid():
            print("\nSiteswap invalid: cannot generate states\n")
            return
        if self.siteswap.isEmpty():
            print("\nSiteswap empty: no states to show.\n")
            return

        self.handler.generateStates(self.siteswap)
        print("Siteswap: " + self.siteswap.getSimpleString())
        print()
        print("States:")
        maxLength = self.siteswap.getMaxStateLength()

        if self.siteswap.isVanilla():
            hand = self.siteswap.getVanillaFirstHand()
            foundValue = False
            index = 0
            if not self.siteswap.isSymmetric():
                length = len(self.siteswap)
            else: 
                length = len(self.siteswap) // 2

            probe = self.siteswap

            while index < length:
                stateString = self.getVanillaStateString(probe) # fix this function

                print('{:<{}}'.format(stateString, maxLength), end = '  --> ')

                if hand == 'r':
                    print(probe.right.getSimpleString())
                    if not probe.right.isNull() and not foundValue:
                        foundValue = True
                    if foundValue:
                        hand = 'l'
                else:
                    print(probe.left.getSimpleString())
                    if not probe.left.isNull() and not foundValue:
                        foundValue = True
                    if foundValue:
                        hand = 'r'

                probe = probe.next

                index +=1
                print()

        else:
            maxLength *= 5

            index = 0
            probe = self.siteswap
            while index < len(self.siteswap):
                print('{:<{}}'.format(str(probe.state), maxLength), end = '  --> ')

                print("(%s,%s)" % (probe.left.getSimpleString(), probe.right.getSimpleString()))
                probe = probe.next
                index +=1
                print()

    def getVanillaStateString(self, siteswap):
            if not siteswap.isVanilla():
                return "attempted to get vanilla state string when not vanilla"
            string = ""
            index = 0
            stateProbe = siteswap.state

            while index < len(siteswap.state) and stateProbe != None:
                if stateProbe.right == 0 and stateProbe.left == 0:
                    string += '0'
                elif stateProbe.right != 0:
                    string += str(stateProbe.right)
                else:
                    string += str(stateProbe.left)    
                index += 1
                stateProbe = stateProbe.next

            return string

    def printHeader(self):
        for i in range(0, get_terminal_size()[0] -1):
            print('*', end = '')

    def printWelcome(self):
        if SiteswapTool.jugglingArt != 6:
            self.printHeader()
            print('{:^{}}'.format("SITESWAP IS FUN!", get_terminal_size()[0]))
            self.printHeader()
        else:
            self.printHeader()
            print('{:^{}}'.format(getArt(self.jugglingArt), get_terminal_size()[0]) +'\n')
            self.printHeader()
        print()

    def chooseSiteswap(self):
        textDict = self.handler.getTextFilesDict()
        print("\nText files found:")
        self.printDict(textDict)
        print("\nEnter file index or 'Enter' to go back: ", end = '')

        # User inputs index option or continues
        while True:
            fileIndex = input()
            # 'Enter' to return
            if fileIndex == '':
                print()
                return

            # File index in range
            elif fileIndex.isdigit() and (int(fileIndex) - 1)  in range(len(textDict)):
                file = open(textDict[int(fileIndex)])
                print("\nSiteswaps in " + textDict[int(fileIndex)] + ":")
                siteswapDict = self.handler.getSiteswapDict(file)
                self.printDict(siteswapDict)


                while True:
                    print("\nEnter siteswap index or 'Enter' to go back: ", end = '')
                    siteswapIndex = input()
                    if siteswapIndex == '': 
                        file.close()
                        print()
                        return

                    elif siteswapIndex.isdigit() and (int(siteswapIndex) - 1) in range(len(siteswapDict)):
                        self.rawSiteswap = siteswapDict[int(siteswapIndex)]
                        if self.handler.parseString(self.rawSiteswap, quiet = False) != False:
                            self.siteswap = self.handler.parseString(siteswapDict[int(siteswapIndex)], quiet = True)
                            self.handler.validate(self.siteswap)
                            self.siteswap.printSiteswap()
                        else:
                            print("Error: siteswap in file not readable by parser. May be bug.\n")
                        file.close()
                        return

                    else: 
                        print("\nInvalid input.")

            else: print("\nInvalid input.")     

    def saveSiteswap(self): # leave this here
        textDict = self.handler.getTextFilesDict()
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
                    siteswapDict = self.handler.getSiteswapDict(file)
                    self.printDict(siteswapDict)

                    file.close()

                    while True:
                        yesno = input("\nWrite to this file? (y/n): ")
                        if yesno == "y" or yesno == "Y":
                            self.handler.writeStrToFile(str(self.rawSiteswap), textDict[int(fileIndex)])
                            print()
                            return
                        else:
                            print()
                            return
                else: print("\nInvalid input.")

    def createNewFile(self):
        fileName = input("\nEnter new file name or press Enter: ")
        if fileName == "":
            print()
            return
        #fileName = fileName.strip() + ".txt"
        fileName += ".txt"
        self.handler.writeStrToFile(str(self.rawSiteswap) + '\n', fileName)
        print("Siteswap saved in " + fileName + '\n')
            
    def pickState(self):
        if self.siteswap.isEmpty():
            print("\nSiteswap empty: no states to display.\n")
            return
        elif not self.siteswap.isValid():
            print("\nSiteswap invalid: cannot generate states.\n")
            return

        self.handler.generateStates(self.siteswap)

        while(True):
            index = input("\nEnter index of state to view: ")
            if index == '':
                print()
                return
            elif index == 'p':
                self.siteswap.printSiteswap()
                continue
            elif not index.isdigit():
                print("\nInvalid input.")
                continue
            elif int(index) in range(0, len(self.siteswap)):
                probe = self.siteswap.getTerm(int(index))
                string = ""
                if self.siteswap.isVanilla():
                    string = self.getVanillaStateString(probe)
                else:
                    string = str(probe.state)
                print()
                print('{:15}{}'.format("Siteswap:", probe.getSimpleString()))
                print('{:15}{}'.format("Current State:", string)) 
                ''' 
                print("\nSiteswap: "+ probe.getSimpleString())
                print("Current State: " + string)
                '''

            else:
                print("\nInvalid input.")

    def printDict(self, dictionary): # format keys - add buffer
        for index in dictionary:
            print('{:4}{}'.format(str(index)+ ":", str(dictionary[index])))

    def printInfo(self):
        self.printHeader()
        print()
        info = \
"""
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