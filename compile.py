import os

print("compiling program to " + __file__ + "\\dist, continue? (ctrl+c to cancel)")
input("")
os.system('pyinstaller --noconfirm --onefile --windowed --add-data "./images;images/"  "./main.py"')