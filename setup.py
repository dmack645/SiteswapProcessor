import subprocess
import siteswapUI
import sys
import os

if sys.executable == None:
    callPython = "python"
else:
    callPython = sys.executable

if os.path.isdir("./venv"):
    #print("Found venv")
    siteswapUI.main(True)
else:
    try:
        subprocess.check_call("{} -m ensurepip --default-pip".format(callPython), shell = True)
        subprocess.check_call("{} -m pip install pyperclip".format(callPython), shell = True)
        siteswapUI.main(True)
    except:
        print("Error installing pip or pyperclip")
        siteswapUI.main(False)





