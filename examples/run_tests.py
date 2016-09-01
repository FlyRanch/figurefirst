import os
#from subprocess import call
examples = [x for x in os.listdir('.') if ('example' in x) and ('.py' in x)]
for example in examples:
	os.system('python %s'%(example))