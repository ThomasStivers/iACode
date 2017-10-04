# Hello world!
# The traditional first project a coder writes in a new language.

def hello(name="world"):
	print "Hello %s!" % name

def helloName():
	name = ""
	print "What is your name?"
	name = raw_input()
	hello(name)

if __name__ == "__main__":
	hello()
	helloName()
	
	
	