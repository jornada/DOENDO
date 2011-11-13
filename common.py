
#  DOENDO - A Python-Based Fortran Refactoring Tool
#  Copyright (C) 2011  Felipe H. da Jornada <jornada@civet.berkeley.edu>

blocks_name = ('program','module','subroutine','type')

def get_elements_with_attrib(root, name, attrib, val):
	'''Return list of element, starting from node root, having tag `name` and
	attribute `attrib`=`val`'''
	elms = root.getElementsByTagName(name)
	elements=[]
	for elm in elms:
		if (elm.getAttribute(attrib) == val):
			elements.append(elm)
	
	return elements
