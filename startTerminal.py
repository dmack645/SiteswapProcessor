import subprocess
try:
    print("WORKED")
    subprocess.call(r'.\start.bat', True)

except:
    print("EXCEPT")
    subprocess.call(r'python siteswapUI.py', False)