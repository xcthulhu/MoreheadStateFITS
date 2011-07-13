#!/usr/bin/python
"""
##############################################################################
Adapted from Lutz' "Programming Python" (2010), Chapter 15, example 15-17
[Simplified, Sandboxed]

Display any CGI server-side script without running it. The filename can
be passed in a URL param or form field (use "localhost" as the server if local):
http://servername/cgi-bin/viewScript.py?filename=somescript.py
Users can cut-and-paste or "View Source" to save file locally.

NOTE: - Uses CGI directory as base 
      - Allows users to view files in CGI directory only

Tested with: Python 2.7.1, Google Chrome 12.0.742.112 for Linux,
             Apache 2.2.17 on Ubuntu 11.04

(Matthew Wampler-Doty, 7/10/2011)
##############################################################################
"""
import cgi, sys
from os.path import dirname

if __name__ == "__main__":
	try:
		form = cgi.FieldStorage()         # URL param or form field
		filename = form['filename'].value
	except:
		filename = 'viewScript.py'        # Default: Show myself

	try:
		assert not dirname(filename)      # *ONLY* CGI scripts allowed
		filetext = open(filename).read()  # platform unicode encoding
	except AssertionError:
		filetext = '(File access denied)'
	except:
		filetext = '(Error opening file: %s)' % sys.exc_info()[1]

	print('Content-type: text/plain\n')
	print(filetext)
