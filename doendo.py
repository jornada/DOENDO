#!/usr/bin/env python

#  DOENDO - A Python-Based Fortran Refactoring Tool
#  Copyright (C) 2011  Felipe H. da Jornada <jornada@civet.berkeley.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import re
import sys
import xml.dom.minidom
import analyze
import rename
from common import *
from optparse import OptionParser

def parse():
	usage='usage: %prog [options] file'
	parser = OptionParser(usage)
	#parser.add_option()
	(options, args) = parser.parse_args()

	if len(args)!=1:
		parser.error('incorrect number of arguments')

	return (options,args)

#TASKS

def task_info(doc, lines):
	analyze.print_info(doc)
	
def task_details(doc, lines):
	print
	print 'Not implemented! How about you implementing this feature?'

def task_auto_rename(doc, lines):
	print
	print 'TASK: Automatically Renaming Single-Letter Variables'
	print '==================================================='

	small_vars = analyze.get_small_vars(doc, 1)
	N = len(small_vars)

	if N==1:
		print
		print 'There are no single-letter variables!'
		print 'Auto-renaming will abort'
		return 
	
	#first, create new names for vars
	new_names=[]
	new_safe=[]
	n=0
	for var in small_vars:
		n+=1
		#new_names.append('%s__%d'%\
		#	(var.getAttribute('name'), n))	
		new_names.append('%s'%\
			(var.getAttribute('name')*2))	
		new_safe.append( analyze.check_var_free(var, new_names[-1]) )

	#this loop is used while the user is manually renaming the vars
	char=''
	while 1:
		#print vars. to be renamed
		last_block=''
		n=0
		print
		print ' The following variables will be renamed'
		print ' ---------------------------------------'
		print
		for var in small_vars:
			n+=1
			block=var.parentNode.getAttribute('name')
			if block!=last_block:
				print ' %s %s'%\
					(blocks_name[int(var.parentNode.getAttribute('type'))],
					block)
				last_block=block
			name = var.getAttribute('name')
			new_name = new_names[n-1]
			if not new_safe[n-1]:
				new_name += '*'
			print '  %5s  %s -> %-3s  ::  %s'%\
				('[%d]'%(n), name, new_name,\
				var.getAttribute('type'))
		if not all(new_safe):
			print
			print ' (* variable name already used)'

		print
		print ' Choose one option:'
		print '    m - manually configure the name of one variable'
		print '    A - accept options and rename'
		print '    q - cancel task'
		char = raw_input(' ')
		if char=='q': return
		elif char=='A':
			if not all(new_safe):
				print ' Note: some varible names are already being used.'
				if raw_input(' Continue [y/n]? ').lower()!='y':
					continue
			break #leave loop and fix vars
		elif char== 'm': pass #we will continue later
		else: continue

		#if got here, configure name of variable
		n=-1
		while (n<0 or n>N):
			char = raw_input(' Choose variable to rename [1-%d, other value to cancel]: '%(N))
			try:
				n = int(char)
			except:
				n = 0
		if n==0: continue

		v_name = small_vars[n-1].getAttribute('name')
		new_name = raw_input(' Enter name for variable %s (leave it empty to cancel): '%(v_name))
		if len(new_name):
			new_names[n-1] = new_name
			new_safe[n-1] = analyze.check_var_free(var, new_name)

	#rename
	renames = dict(zip(small_vars, new_names))
	rename.rename(lines, doc, renames)
	print
	print ' Rename complete!'
	#save
	import os.path
	fname = doc.childNodes[0].nodeName
	(head,tail) = os.path.split(fname)
	tail = 'doendo_'+tail
	new_fname = os.path.join(head,tail)
	print ' Writing %s'%(new_fname)
	fout = open(new_fname,'w')
	fout.write(''.join(lines))
	fout.close()	

def task_manual(doc, lines):
	print
	print 'Not implemented! How about you implementing this feature?'


def task_loop(doc, lines):
	tasks = {
		'i': task_info,
		'd': task_details,
		'a': task_auto_rename,
		'm': task_manual,
		'q': None
		}

	char=''
	while not (char in tasks.keys()):
		print
		print 'Please choose one task'
		print '   i - show brief info about the source code'
		print '   d - show detailed info about the source code'
		print '   a - automatically rename single-letter variables'
		print '   m - manually rename variables'
		print '   q - quit'
		char = raw_input('')

	if char=='q':
		print
		sys.exit()

	#call the function
	tasks[char](doc, lines)

	return char

def main():
	(options, args) = parse()

	print '''
==========================================================================
  Welcome to DOENDO - the tool that makes your FORTRAN code less painful   
              DOENDO Copyright (C) 2011  Felipe H. da Jornada
              This program comes with ABSOLUTELY NO WARRANTY.
=========================================================================='''

	fname = sys.argv[1]
	fin = open(fname)
	lines = fin.readlines()
	fin.close()

	#need file as single character string
	data = ''.join(lines)

	#prepare DOM of source code
	doc = analyze.analyze(fname, data)
	#print useful info about code (get small variables for free)
	small_vars = analyze.print_info(doc)

	while (1):
		task_loop(doc, lines)


if __name__=='__main__':
	main()
