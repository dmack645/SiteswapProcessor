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
        subprocess.check_call("{} -m venv venv".format(callPython), shell = True)
        subprocess.check_call([callPython, "-m", "pip", "install", "pyperclip"])
        siteswapUI.main(True)
    except:
        print("Error installing pip or initializing venv")
        siteswapUI.main(False)





