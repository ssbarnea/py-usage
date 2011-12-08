from __future__ import absolute_import

import logging, os, sys, inspect

debug = False

#if __name__ == '__main__':
if debug:
	print "cwd=", os.getcwd()
	print "sys.argv[0]", sys.argv[0]
try:
	if debug:
		print "__file__", __file__
		print "abspath(__file__)", os.path.abspath(__file__)
	my_location = os.path.dirname(os.path.abspath(__file__))
except:
	if debug:
		print "__file__ is not defined"
my_location = os.path.dirname(os.path.abspath(inspect.getfile( inspect.currentframe())))

if debug:
	print "inspect", inspect.getfile( inspect.currentframe())
	print "inspect: ", os.path.dirname(inspect.getfile( inspect.currentframe() ))
	print "dir=", os.path.dirname(os.path.join(os.getcwd(), sys.argv[0]))

print my_location
