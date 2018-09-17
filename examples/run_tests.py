#! /usr/bin/python
import os
#from subprocess import call
examples = [x for x in os.listdir('.') if ('example' in x) and ('.py' in x)]
print('########################')
print('#   Testing Python2    #')
print('########################')
for example in examples:
	print("Running:%s"%example)
	os.system('python2 %s'%(example))

print('########################')
print('#   Testing Python3    #')
print('########################')
for example in examples:
	print("Running:%s"%example)
	os.system('python %s'%(example))