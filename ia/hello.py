# Hello world!
# Copyright (C) 2017 Thomas Stivers
# Released under the GNU Public License Version 2.
#
# The traditional first project a coder writes in a new language.

# The sys module contains command line arguments.
import sys

def hello(name="world"):
	"""In python functions are typically documented with a documentation string which can be reached from within code. This one will be found in the hello.__doc__ property"""
	if len(sys.argv) == 2:
		name = sys.argv[1]
	print ("Hello {0}!".format(name))

def helloName():
	"""Gets a name from the user and passes it to the hello() function."""
	name = raw_input("What is your name? ")
	hello(name)

# In python code can be imported or run directly. If the __name__ variable is
# set to "__main__" we know that this code was run directly and not imported as a library.
if __name__ == "__main__":
	hello()
	helloName()

# Sample output
#
# Script started on Sat, Oct  7, 2017  7:45:27 AM
#
# thoma@disco-stu ~/git/iACode
# $ python hello.py
# Hello world!
# What is your name?
# Thomas
# Hello Thomas!
#
# thoma@disco-stu ~/git/iACode
# $ python
# Python 2.7.13 (default, Mar 13 2017, 20:56:15)
# [GCC 5.4.0] on cygwin
# Type "help", "copyright", "credits" or "license" for more information.
# >>> import hello
# >>> hello.hello("Thomas")
# Hello Thomas!
# >>> hello.helloName()
# What is your name?
# Thomas
# Hello Thomas!
# >>> from hello import *
# >>> hello()
# Hello world!
# >>> helloName()
# What is your name?
# Thomas
# Hello Thomas!
# >>> exit()
#
# thoma@disco-stu ~/git/iACode
# $ exit
# exit
#
# Script done on Sat, Oct	 7, 2017  7:47:54 AM
