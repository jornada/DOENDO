#!/usr/bin/env python

import re
import sys
import xml.dom.minidom
import analyze
import rename

if len(sys.argv)<5:
	print 'Usage: %s file scope orig_var new_var'%(sys.argv[0])
	sys.exit(1)

fname = sys.argv[1]
scope = sys.argv[2]
orig_var = sys.argv[3]
new_var = sys.argv[4]

fin = open(fname)
lines = fin.readlines()
fin.close()

data = ''.join(lines)

#analyze
doc = analyze.analyze(fname, data)

#rename
rename.rename(lines, doc, scope, {orig_var:new_var})

print ''.join(lines)
