
#  DOENDO - A Python-Based Fortran Refactoring Tool
#  Copyright (C) 2011  Felipe H. da Jornada <jornada@civet.berkeley.edu>

import re
import xml.dom.minidom
import analyze
import common

def rename(lines, doc, ren_dict, block=None):
	'''
	Rename a variable in a particular block

	lines: line-oriented buffer to be altered
	doc: DOM object containing info about code
	ren_dict: dictionary of renames. This can be a map of string->strings
	or node->string.
	block: routine/module/sub to work in. None means the root node.
	This property only makes sense if you specified the ren_dict as a map 
	of string->string, otherwise the routine know the block in which it should
	work automatically.

	Example:
		fname = 'file.f90'
		lines = open(fname).readlines()
		doc = analyze(fname, ''.join(lines))
		rename(lines, doc, {'i':'ii'})
	'''

	if block is None:
		el = doc.childNodes[0]
	else:
		els = doc.getElementsByTagName('block')
		el=None
		for el_ in els:
			if el_.getAttribute('name')==block:
				el=el_
				break

	if el is None:
		print 'Could not find block '+block
		return

	for var0, new_var in ren_dict.iteritems():
		if isinstance(var0, str):
			orig_var = var0
			_vars = el.getElementsByTagName('var')
			var=None
			for var_ in _vars:
				if var_.getAttribute('name')==orig_var:
					var=var_
					break
		else:
			var = var0
			el = var.parentNode
			orig_var = var.getAttribute('name')

		if var is None:
			print 'Could not find variable '+orig_var+' in block '+block
			sys.exit(1)

		#get the initial and final lines
		start = int(el.getAttribute('start'))
		end = int(el.getAttribute('end'))

		#this will match only variables
		cmp_obj = re.compile(r'^([^!]*[^a-zA-Z0-9_!%%])%s([^a-zA-Z0-9_!%%])'%(orig_var))
		subs_str=r'\1%s\2'%(new_var)
		for i in range(start, end+1):
			old_line = ''
			new_line = ' '+lines[i]
			#hack to do multiple substitution on the same line
			#I probablly need to learn more regexp..
			while old_line != new_line:
				old_line = new_line
				new_line = cmp_obj.sub(subs_str, old_line)
			lines[i] = new_line[1:]

	#re-analyze file
	fname = doc.childNodes[0].nodeName
	data = ''.join(lines)
	doc = analyze.analyze(fname, data)

