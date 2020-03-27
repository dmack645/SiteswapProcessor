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
Notes should go here   
***************************************************************************

Scan computer for JugglingLab.exe and use that instead of browser if exists
""" 



"""
TODO
ADD DELETE/INSERT/MOVE FEATURE FOR TXT FILES
CONVERT FROM MHN STRUCTURE TO STRING IN JLAB NOTATION 


Program can run .bat files to use command prompt. (echo off)
select state and generate possible transitions into/out of pattern (select period)

Fix parser to not allow 0 in multiplex throw(as first [012] or otherwise [12303])
strip user input of lagging whitespace

Right now, the parser adds an implied null beat whenever '-' is not in term
When entering an MHN, this causes problems when there isn't a null throw in a term.
I think this is ok for now unless I come up with something better. Just use "!"" when needed

There should be a showDiagnostics mode. Additional information printed, such as whether the validator converted it to symmetric
mhn mode: everything is in mhn. No simplified display of state or siteswap

BUG: raw input: (6x,[4 0x])!(-,-)(0,2x)!(-,-)(4x,ax)!(-,-)(2x,4 )!(-,-)
    swap 0l0 3l0 should yield:  
    Valid 4-prop siteswap
    Indices:       (    0    )( 1 )( 2  )( 3  )(  4  )( 5 )( 6  )( 7 )
    Siteswap:      (3x,[4 0x])(-,-)(0,2x)(3 ,-)(4x,ax)(-,-)(2x,4)(-,-)
    Rethrow line:  (0x,[4x2x])(-,-)(0,4 )(3x,-)(2x,4 )(-,-)(ax,3)(-,-)

but with raw input (6x,[40x])(0,2x)(4x,ax)(2x,4) I'm getting :
    Valid 5-prop siteswap
    Indices:       (    0    )( 1  )( 2  )( 3  )(  4  )( 5  )( 6  )( 7  )
    Siteswap:      (3x,[4 0x])(3 ,-)(0,2x)(3 ,-)(4x,ax)(3 ,-)(2x,4)(3 ,-)
    Rethrow line:  (0x,[4x3 ])(3x,-)(0,4 )(3x,-)(2x,4 )(3x,-)(ax,3)(3x,-)

    It says it's valid but it is not. The validator appears to be working fine.
    The issue might be with how the parser accounts for implicit null beats.
    Solved:
    There's an issue with default parameters of the Siteswap constructor. Must manually construct/pass null throwNode objects
fix formatting error with invalid rethrow line ([44x],2)(4,2x)
"""
import sys


from siteswapParser import Parser
from siteswap import Siteswap
from stateGenerator import StateGenerator
import os
import webbrowser
from terminalSize import get_terminal_size
from asciiArt import getArt
from siteswapHandler import SiteswapHandler
from copy import deepcopy
import re
import pyperclip



class SiteswapUI(object):
    jugglingArt = 6 
    def __init__(self, venv = False):
        self.venv = venv
        self.rawSiteswap = ''
        self.printWelcome()

        self.siteswap = Siteswap()     
        self.previousSiteswaps = list()

        self.dwell = 1.3

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

            elif userString == 'ps':
                print(self.getSimpleString(self.siteswap, True) + '\n')

            elif userString == 'sr' or userString == 'sl':
                self.siteswap = self.handler.shift(self.siteswap, userString)
                self.siteswap.printSiteswap()
            
            elif userString == 'states':
                self.printStates()

            elif userString == 'state':
                self.pickState()

            elif userString == 'ba':
                if len(self.previousSiteswaps) > 1:
                    self.siteswap = self.previousSiteswaps.pop()
                    self.rawSiteswap = self.getRawInputString(self.siteswap)
                    self.siteswap.printSiteswap()
                else:
                    print("\nNo previous siteswaps to load.\n")

            elif userString == 'a':
                jLab = self.getJlabString(self.siteswap)
                url = "https://jugglinglab.org/anim?pattern=" + jLab
                #url += ";gravity=2500.0;bps=6.5"
                webbrowser.open_new_tab(url)
                print("\nAttempting to load Juggling Lab gif in default browser.")
                print("Siteswap string: " + jLab + '\n')

            elif userString == 'jlab':
                #print("Current pattern in Juggling Lab compatible siteswap notation: ")
                string = self.getJlabString(self.siteswap)
                print("\nJuggling Lab compatible: " + string + '\n')
                if self.venv:
                    pyperclip.copy(string)

            elif re.match(r'swa?p?\s+([0-9][0-9]?)([rRlL])([0-9][0-9]?)\s+([0-9][0-9]?)([rRlL])([0-9][0-9]?)\s*', userString) != None:
                swapRE = re.search(r'swa?p?\s+([0-9][0-9]?)([rRlL])([0-9][0-9]?)\s+([0-9][0-9]?)([rRlL])([0-9][0-9]?)\s*', userString)
                term1 = int(swapRE.group(1))
                hand1 = swapRE.group(2).lower()
                throw1 = int(swapRE.group(3))
                term2 = int(swapRE.group(4))
                hand2 = swapRE.group(5).lower()
                throw2 = int(swapRE.group(6))
                if (not term1 < len(self.siteswap)) or (not term2 < len(self.siteswap)): 
                    print("One or more of the term indices provided is out of range.\n")
                    self.printHeader()
                    continue
                self.previousSiteswaps.append(deepcopy(self.siteswap))
                self.siteswap = self.handler.swap(self.siteswap, term1, hand1, throw1, term2, hand2, throw2)
                self.siteswap.printSiteswap()
                self.rawSiteswap = self.getRawInputString(self.siteswap)

            else:
                if self.handler.parseString(userString, quiet = False) != False:
                    self.rawSiteswap = userString
                    self.previousSiteswaps.append(deepcopy(self.siteswap))
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
        print("\nSiteswap: " + self.getSimpleString(self.siteswap))
        print()
        print("States:")
        maxLength = self.siteswap.getMax()

        # Vanilla
        if self.siteswap.isVanilla():
            hand = self.handler.getVanillaFirstHand(self.siteswap)
            index = self.handler.getVanillaFirstIndex(self.siteswap)

            # Get first hand 
            while index != 0:
                if hand == 'r':
                    hand = 'l'
                elif hand == 'l':
                    hand = 'r'
                index -= 1

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
                    hand = 'l'
                else:
                    print(probe.left.getSimpleString())
                    hand = 'r'

                probe = probe.next
                index += 1
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
        if SiteswapUI.jugglingArt != 6:
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
                            self.previousSiteswaps.append(deepcopy(self.siteswap))
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
        self.handler.writeStrToFile(str(self.rawSiteswap), fileName)
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
                print('{:15}{}'.format("Siteswap:", self.getSimpleString(probe)))
                print('{:15}{}'.format("Current State:", string)) 

                '''
                temp = self.siteswap
                self.siteswap = self.siteswap.getTerm(int(index))

                string = ""
                if self.siteswap.isVanilla():
                    string = self.getVanillaStateString(self.siteswap)
                else:
                    string = str(self.siteswap.state)
                print()
                print('{:15}{}'.format("Siteswap:", self.getSimpleString()))
                print('{:15}{}'.format("Current State:", string)) 
                self.siteswap = temp
                '''


            else:
                print("\nInvalid input.")

    def printDict(self, dictionary): # format keys - add buffer
        for index in dictionary:
            print('{:4}{}'.format(str(index)+ ":", str(dictionary[index])), end = "")
            if self.handler.parseString(str(dictionary[index])) != False:
                temp = self.handler.parseString(str(dictionary[index]))
                self.handler.validate(temp)
                if not temp.isValid():
                    print("  INVALID", end = "")
            print()

    def getSimpleString(self, siteswap, mhn = False):
        """Returns a string representation of the structure in MHN format"""


        if siteswap.isVanilla() and not mhn:
            return self.getJlabString(siteswap)
        else:
            string = ""

            index = 0
            probe = siteswap
            while index < len(siteswap):
                string += ("(%s,%s)" % (probe.left.getSimpleString(), probe.right.getSimpleString()))
                probe = probe.next
                index += 1
            return string

    def getJlabString(self, siteswap):
        """Returns a string representation of the structure in JLAB format"""
        string = ""
        index = 0


        if siteswap.isVanilla():
            hand = self.handler.getVanillaFirstHand(siteswap)
            firstIndex = self.handler.getVanillaFirstIndex(siteswap)

            # get first term hand 
            while firstIndex != 0:
                firstIndex -= 1
                if hand == 'r':
                    hand = 'l'
                else:
                    hand = 'r'

            if siteswap.isSymmetric(): # SHOULDN'T NEED .SYMMETRIC. JUST ISSYMMETRIC IN HANDLER~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                patternLength = len(siteswap) // 2
            else:
                patternLength = len(siteswap)

            probe = siteswap
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

        elif siteswap.isSimpleSync():
            probe = siteswap
            # point to first term that isn't a null beat
            while True:
                if probe.left.throw != None or probe.right.throw != None:
                    break
                probe = probe.next

            throwBeat = True
            index = 0
            if siteswap.isSymmetric():
                length = len(siteswap) // 2
            else:
                length = len(siteswap)
            while index < length:
                if not throwBeat:
                    probe = probe.next
                    index += 1
                    throwBeat = True
                    continue
                if probe.left.getSimpleString() == '-':
                    left = '0'
                else:
                    left = probe.left.getSimpleString()
                if probe.right.getSimpleString() == '-':
                    right = '0'
                else:
                    right = probe.right.getSimpleString()
                string += ("(%s,%s)" % (left, right))   
                probe = probe.next
                index += 1
                throwBeat = False
            if siteswap.isSymmetric():
                string += "*"   
            return string      

        else:
            for term in siteswap:   # REVISE THIS TO USE PROBE~~~~~~~~~~~~
                if term.left.getSimpleString() == '-':
                    left = '0'
                else:
                    left = term.left.getSimpleString()
                if term.right.getSimpleString() == '-':
                    right = '0'
                else:
                    right = term.right.getSimpleString()
                string += ("(%s,%s)!" % (left, right))
            return string

    def getRawInputString(self,siteswap):
        """Returns a string representation of the structure in MHN format"""
        if siteswap.isVanilla():
            return self.getJlabString(siteswap)
        else:
            string = ""

            index = 0
            probe = siteswap
            while index < len(siteswap):
                string += ("(%s,%s)!" % (probe.left.getSimpleString(), probe.right.getSimpleString()))
                probe = probe.next
                index += 1
            return string

    def printInfo(self):
        try:
            file = open("info.txt", 'r')
        except:
            print("\nCould not open or find info.txt\n")
            return
        print()
        self.printHeader()
        print('\n')
        for line in file:
            print(line, end = '')
        print()


def main():
    try:
        import pyperclip
        generator = SiteswapUI(True)
    except:
        print("Failed to load virtual environment.")
        generator = SiteswapUI()

    generator.run()

if __name__ == "__main__": main()
