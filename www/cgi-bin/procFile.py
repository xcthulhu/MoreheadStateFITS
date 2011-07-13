#!/usr/bin/python
"""
################################################################################
Adapted from Lutz' "Programming Python", Chapter 15, Example 15-30

Extract file uploaded by HTTP from web browser; 

Users visit archive-file.html to get the upload form page, 
which then triggers this script on server. 

We append timestamps to files before archiving, check for collisions

Only works if archive dir and subdirs are writable.
Unix command 'chmod 777 <dirname>' will generally ensure this

File pathnames may arrive in client's path format - this is handled here.

Tested with: Python 2.7.1, Google Chrome 12.0.742.112 for Linux,
             Apache 2.2.17 on Ubuntu 11.04

(Matthew Wampler-Doty, 7/10/2011)
################################################################################
"""

import cgi, os, sys, time, fitsproc
import posixpath, ntpath, macpath   # for client paths
debugmode = False                   # True=print form info
archivedir = '../archive'           # Archive Directory

# Platform independent basename function
def basename(origpath):
	for pathmodule in [posixpath, ntpath, macpath]:   # get file at end
		bname = pathmodule.split(origpath)[1]  # try all clients
	if bname != origpath:                          # may be any server
		return bname                           # lets spaces pass
	return origpath                                   # failed or no dirs

def rename(fn,band,sigma):
	tm = time.gmtime()
	newfn = "%i%i%i%i%i%i-%s-%s-%s" % (tm.tm_year, tm.tm_mon, tm.tm_mday,\
                                           tm.tm_hour, tm.tm_min, tm.tm_sec,\
                                           band, sigma, fn)
	arch = os.path.join(archivedir, "RAW", "%i" % tm.tm_year, newfn)
	archfn,archext = os.path.splitext(arch)
	archfn_ = os.path.split(arch)[1]
	if archext == '':
		fits = os.path.join(archivedir, "FITS",
                                    "%i" % tm.tm_year,
                                    archfn_ + '.fits')
	else:
		fits = os.path.join(archivedir, "FITS",
                                    "%i" % tm.tm_year,
                                    archfn_.replace(archext,'.fits'))
	fitsfn,fitsext = os.path.splitext(fits)
	if (os.path.lexists(arch) \
            or os.path.lexists(fits)):
		i = 1
		archfn,archext = os.path.splitext(arch)
		fitsfn,fitsext = os.path.splitext(fits)
		while (os.path.lexists(archfn + "(%i)" % i + archext)\
                       or os.path.lexists(fitsfn + "(%i)" % i + fitsext)) :
			i += 1
		return archfn + "(%i)" % i + archext,\
        	       fitsfn + "(%i)" % i + fitsext
	else:
		return arch,fits

def saveonserver(fname,band,sigma):              # use file input form data
	archname,fitsname = rename(fname,band,sigma)

	# Create parent directories if necessary
	archpth = os.path.split(archname)[0]
	fitspth = os.path.split(fitsname)[0]

	if (not os.path.exists(archpth)):
		os.makedirs(archpth)
	if (not os.path.exists(fitspth)):
		os.makedirs(fitspth)

	srvrfile = open(archname, 'wb')               # always write bytes here
	srvrfile.write(fileinfo.value)                # save in server file
	srvrfile.close()
	os.chmod(archname, 0o666)         # make writable: owned by 'nobody'
	fitsproc.fitsProc(archname, band, sigma, fitsname)
	os.chmod(fitsname, 0o666)         
	return archname, fitsname

def mklink(pth):
	return "<a href=\"%s\">%s</a>" % (pth, pth.replace("../",""))

if __name__ == "__main__":
	# Two outputs: one for success and one for failure
	goodhtml = """
<html><title>'%(fname)s' Processed</title>
<body>
	<h1>File '%(fname)s' Processed</h1>
	Saved an archive file to: %(archlink)s<br>
	Created processed FITS file: %(fitslink)s<br>
	<p>Band: %(band)s<br>
	Sigma: %(sigma)s
</body></html>"""

	failhtml = """
<html><title>FAIL</title>
<body>
	<h1>Failed to Process File</h1>
	Reason: %s
</body></html>"""

	sys.stderr = sys.stdout            # show error msgs
	form = cgi.FieldStorage()          # parse form data
	print("Content-type: text/html\n") # with blank line
	if debugmode: cgi.print_form(form) # print form fields

	# Collect useful data for our form
	data = {}

	# There are a lot of ways to be broken
	errors = ""

	# Broken filename
	if not 'clientfile' in form:
		errors += '<p>Error: no file was received'

	if not form['clientfile'].filename:
		errors += '<p>Error: filename is missing'
	else:
		data['fname'] = cgi.escape(basename(form['clientfile'].filename))

	# Broken band
	if not 'band' in form: # note: not really possible by design
		errors += '<p>Error: band specification is missing'
	else:
		data['band'] = form['band'].value

	# Broken sigma
	if not 'sigma' in form:
		errors += '<p>Error: <i>standard deviation</i> (Sigma) for Gaussian filter is missing'
	else:
		try:
			data['sigma'] = float(form['sigma'].value)
		except:
			errors += 'Error: %s<p>%s<p>[in processing <i>standard deviation</i> (Sigma) for Gaussian filter]' % tuple(sys.exc_info()[:2])

	if errors:
		print(failhtml % errors) 
	else:
		fileinfo = form['clientfile']
		try:
			archname,fitsname = saveonserver(**data)
		except:
			errmsg = '%s<p>%s' % tuple(sys.exc_info()[:2])
			print(failhtml % errmsg)
		else:
			data['archlink'] = mklink(cgi.escape(archname))
			data['fitslink'] = mklink(cgi.escape(fitsname))
			print(goodhtml % data)
