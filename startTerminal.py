import subprocess
try:
    subprocess.call(r'.\start.bat', True)
except:
    print("EXCEPT")
    subprocess.call(r'python siteswapUI.py', False)