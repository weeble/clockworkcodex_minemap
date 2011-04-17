import sys
import os.path

if sys.version_info<(2,6):
    print ("Warning: This hasn't been tested with your version of Python. Try Python 2.7.")

if sys.version_info>=(3,0):
    print ("Error: This program cannot run in Python 3.0+. Try Python 2.7.")
    sys.exit(1)

required_modules = [
    ('setuptools', False, 'Got to http://pypi.python.org/pypi/setuptools for instructions.', 'This lets you install other Python modules easily.'),
    ('numpy', True, 'easy_install numpy', 'This performs efficient processing of large arrays of numbers.'),
    ('PyOpenGL', True, 'easy_install PyOpenGL', 'This allows using a graphics card for rendering.'),
    ('pygame', True, 'easy_install pygame', 'This creates windows on the screen and manages input.'),
    ('nbt', True, 'easy_install nbt', 'This parses Minecraft\'s NBT file format.')]

missing_modules = []

try:
    import setuptools
except ImportError:
    missing_modules.append('setuptools')

try:
    import numpy
except ImportError:
    missing_modules.append('numpy')

try:
    import OpenGL
except ImportError:
    missing_modules.append('PyOpenGL')

try:
    import pygame
except ImportError:
    missing_modules.append('pygame')

try:
    import nbt
except ImportError:
    missing_modules.append('nbt')

critical_missing_modules = [name for (name, critical, advice, info) in required_modules if name in missing_modules and critical]

if (len(critical_missing_modules)>0):
    print ("Some modules are missing. You need to install them first.")
    for name, critical, advice, info in required_modules:
        if name in missing_modules:
            print ("")
            print ("I couldn't find '%s'." % name)
            print (info)
            print ("To install it, try this:")
            print ("    " + advice)
    sys.exit(1)

if not os.path.exists('world/region/r.0.0.mcr'):
    print ("Missing file - you need to put r.0.0.mcr in the folder world/region")
    sys.exit(1)

if not os.path.exists('terrain.png'):
    print ("Missing file - you need to have terrain.png in the current directory.")

import mapfun
del pygame.mixer
mapfun.x()
print "display.quit"
pygame.display.quit()
print "mixer.quit"
#pygame.mixer.quit()
print "pygame.quit"
pygame.quit()
print "end"
sys.exit(0)
