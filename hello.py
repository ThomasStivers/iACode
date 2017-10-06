# Hello world!
# The traditional first project a coder writes in a new language.

def hello(name="world"):
	"""In python functions are typically documented with a documentation string which can be reached from within code."""
	print "Hello %s!" % name

def helloName():
	"""Gets a name from the user and passes it to the hello() function."""
	name = ""
	print "What is your name?"
	name = raw_input()
	hello(name)

# In python code can be imported or run directly. If the __name__ variable is
# set to "__main__" we know that this code was run directly and not imported as a library.
if __name__ == "__main__":
	hello()
	helloName()