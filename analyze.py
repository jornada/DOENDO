#!/usr/bin/env python

#  DOENDO - A Python-Based Fortran Refactoring Tool
#  Copyright (C) 2011  Felipe H. da Jornada <jornada@civet.berkeley.edu>

import re
import xml.dom.minidom
from common import *

def analyze(name, data):
	'''Parses a FORTRAN source file and returns a XML document
	name: name of the file
	data: string containing all the file
	'''

	def find_token(_cmp, line):
		res = _cmp.search(line)
		if not res is None:
			return res.group(0)
		else: return None

	doc = xml.dom.minidom.Document()
	cur_node = doc.createElement(name)
	doc.appendChild(cur_node)

	#used to match the "blocks"
	re_start = (re.compile('^program (\w+)'),
		re.compile('^module (\w+)'),
		re.compile('^subroutine (\w+)'),
		re.compile('^type (\w+)') )

	re_end = (re.compile('end program (\w+)'),
		re.compile('end module (\w+)'),
		re.compile('end subroutine (\w+)'),
		re.compile('end type (\w+)') )

	#get corrected line number (b/c we joined lines ending with &)
	offsets=[]
	for m in re.finditer('&[ ]*\n', data, re.MULTILINE):
		start = m.start()
		offsets.append( data.count('\n',0,start) )

	no_multi_lines = re.sub('&[ ]*\n', '', data, re.MULTILINE)
	line_n = -1
	cur_node.setAttribute('start','0')
	for line in no_multi_lines.split('\n'):
		line_n += 1
		#correct line number
		while line_n-1 in offsets:
			line_n += 1

		#clean-up useless spaces and comments
		line = re.sub(r'!.*','',line)
		line = re.sub(r'[ ]+',' ',line)
		line = re.sub(r'[ ]*::[ ]*','::',line)
		line = re.sub(r'[ ]*,[ ]*',',',line)
		line = re.sub(r'^ ','',line)
		line = re.sub(r' $','',line)

		if not len(line):
			continue

		#determine if we are starting/closing a block
		#ending program|module|subroutine|type ?
		token=None
		for re_obj in re_end:
			token = find_token(re_obj, line)
			if token: break
		if not(token is None):
			cur_node.setAttribute('end',str(line_n))
			cur_node = cur_node.parentNode
			
		else:
			#starting program|module|subroutine|type ?
			i=0
			for re_obj in re_start:
				token = find_token(re_obj, line)
				if token: break
				i+=1
			if not(token is None):
				tmp_node = doc.createElement('block')
				cur_node.appendChild(tmp_node)
				cur_node = tmp_node
				cur_node.setAttribute('start',str(line_n))
				cur_node.setAttribute('type',str(i))
				cur_node.setAttribute('name',token.split(' ')[-1])

		#now, search for vars
		has_vars = '::' in line
		if has_vars:
			col_pos = line.index('::')
			var_type = line[:col_pos]
			var_str = line[col_pos+2:]
			#trowing away array indices
			#TODO: store this information as a sulfix
			var_str = re.sub(r'\([^\)]*\)','',var_str)
			for v in var_str.split(','):
				var_node = doc.createElement('var')
				var_node.setAttribute('type',var_type)
				var_node.setAttribute('name',v)
				#var_node.setAttribute('sulfix', blah)
				cur_node.appendChild(var_node)

	cur_node.setAttribute('end',str(line_n-1))
	return doc

def get_small_vars(doc, ignore_types=True, len_small=1):
	'''Return list of variables that have only one letter'''

	_vars = doc.getElementsByTagName('var')
	small_vars = []
	for var in _vars:
		name = var.getAttribute('name')
		if len(name) <= len_small:
			#if appropriate, ignore vars inside types
			if (var.parentNode.getAttribute('type')!='3') or \
			   (not ignore_types):
				small_vars.append(var)
	return small_vars

def check_var_free(elem, name):
	'''Check if `name` is not a variable in the scope of `elem` or its parents'''

	el = elem
	while el!=None:
		for child in el.childNodes:
			if child.nodeName=='var':
				if child.getAttribute('name')==name:
					return False
		try:
			el = el.parentNode
		except:
			el = None
	return True

def print_info(doc):
	print
	print 'Some useful info:'
	is_prog=False
	node0 = doc.childNodes[0]
	print ' - Source file name:', node0.nodeName
	if len(node0.childNodes):
		is_prog = node0.childNodes[0].getAttribute('type')=='0'
	print ' - Is this a program?', is_prog
	modules = get_elements_with_attrib(doc, 'block', 'type', '1')
	print ' - Number of modules:', len(modules)
	subs = get_elements_with_attrib(doc, 'block', 'type', '2')
	print ' - Number of subroutines:', len(subs)
	types = get_elements_with_attrib(doc, 'block', 'type', '3')
	print ' - Number of types:', len(types)
	all_vars = doc.getElementsByTagName('var')
	print ' - Number of variables:', len(all_vars)
	small_vars = get_small_vars(doc, 1)
	print ' - Single letter vars:', len(small_vars)
	return small_vars

if __name__=='__main__':
	import sys
	fname = sys.argv[1]
	lines = open(fname).read()
	doc = analyze(fname, lines)
	print
	print doc.toprettyxml()

