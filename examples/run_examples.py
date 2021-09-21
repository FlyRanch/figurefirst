#!/usr/bin/env python
import os
from glob import glob

# from subprocess import call
examples = glob(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "example_*.py")
)
print("########################")
print("#   Testing Python2    #")
print("########################")
for example in examples:
    print("Running:%s" % example)
    os.system("python2 %s" % (example))

print("########################")
print("#   Testing Python3    #")
print("########################")
for example in examples:
    print("Running:%s" % example)
    os.system("python %s" % (example))
