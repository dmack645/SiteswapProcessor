import subprocess
import siteswapUI

try:
    
    subprocess.call(r'.\start.bat')

except:
    print("Failed to load start.bat from startTerminal.py")
    siteswapUI.main(False)