#!/usr/bin/env python

import sys, os, pyfits, csv
from scipy.ndimage import gaussian_filter
import numpy as np

def test():
	print "test"

def getData(filename):
    "Gets RA, DEC, LST, and Voltage data from a filename"
    # Load the tsv file
    fp = open(filename, 'rb')
    data = csv.reader(fp, delimiter='\t')

    # Thow away header data
    data.next()

    # Extract RA, DEC, LST, and Voltage from the raw data
    # We use a list comprehension
    ra,dec,lst,voltage = np.transpose(
        np.array([np.array([float(row[14]),
                            float(row[15]),
                            float(row[16]),
                            float(row[17])]) 
                  for row in data]))

    # Close filepointer and return
    fp.close()
    return [ra,dec,lst,voltage]

def celestialToImage(ra,dec,voltage,cdelt=1):
    """Converts celestial data to an image.
    Input:
    - 3 data series of the same size: the right ascension, the declination and the voltage
    - The size of a pixel cdelt (default is 1).

    Outputs 3-tuple of (raref,decref,sz,img) where:
    - (ra,dec) are the reference coordinates of the lower left hand corner
    - sz is an integer representing the size of an edge of the image
    - img is the actual image data"""

    # Reference coordinates are the minimal values, 
    # which correspond to the lower left hand corner
    raref, decref = min(ra), min(dec)

    # The size of an edge of the image (forced to be square)
    sz = int(np.ceil(max((max(ra)-raref),(max(dec)-decref))*cdelt))

    # Create an image from the data
    img = np.zeros((sz,sz),np.float64)
    for (r, d, v) in zip(ra,dec,voltage):
        img[cdelt*(r-raref),cdelt*(d-decref)] = v

    return (raref,decref,sz,img)

def fitsProc(filename,bandname,sigma,newfn=""):
    "Makes a FITS file from a filename with a specified bandwidth"

    # Determine the band from the bandname argument
    if bandname.lower() == "ku": cdelt = 133.33
    elif bandname.lower() == "l": cdelt = 6.8966
    else: raise RuntimeError('Unsupported band-name')

    ra,dec,lst,voltage = getData(filename)

    # The following is taken from the Dutch PyFITS tutorial here:
    # http://www.astro.rug.nl/~belikov/VO2010/Werkcolleges/W5/Pyfits_tutorial.pdf
    # Make a FITS table HDU from the data series
    cRA=pyfits.Column(name='RA', format='D', array=ra)
    cDEC=pyfits.Column(name='DEC', format='D', array=dec)
    cLST=pyfits.Column(name='LST', format='D', array=lst)
    cVoltage=pyfits.Column(name='Voltage', format='D', array=voltage)
    cs=pyfits.ColDefs([cRA,cDEC,cLST,cVoltage])
    table_hdu=pyfits.new_table(cs)

    # Make the image
    raref,decref,sz,img = celestialToImage(ra,dec,voltage,cdelt)

    # Apply a Guassian Filter
    img = gaussian_filter(img, sigma=(sigma, sigma), mode='constant', cval=0.0)

    # Create the abstract FITS file from the image
    hdu=pyfits.PrimaryHDU(img)
    hdu.header.update('naxis',2,'Two dimensional image')
    hdu.header.update('naxis1', sz,'Width of image')
    hdu.header.update('naxis2', sz,'Heigth of image')
    hdulist=pyfits.HDUList([hdu])
    hdulist.append(table_hdu)

    # Define the FITS header
    prihdr = hdulist[0].header
    prihdr.update('crval1', raref,'Reference longitude')
    prihdr.update('crval2', decref,'Reference latitude')
    prihdr.update('radesys', 'FK5     ','Coordinate system ')
    prihdr.update('equinox', 2000.0,'Epoch of the equinox')
    prihdr.update('ctype1', 'RA---TAN','Coordinates -- projection')
    prihdr.update('ctype2', 'DEC--TAN','Coordinates -- projection')
    prihdr.update('crpix1', 0,'X reference pixel')
    prihdr.update('crpix2', 0,'Y reference pixel')
    prihdr.update('cdelt1', cdelt,'X scale')
    prihdr.update('cdelt2', cdelt,'Y scale')

    # Check for Sanity
    hdulist.verify()

    # Get new datafile name from filename
    if newfn == "":
       ext = os.path.splitext(filename)[1]
       if ext == '':
          newfn = filename + '.fits'
       else:
          newfn = filename.replace(ext,'.fits')

    # Avoid file collisions by simple loop
    while os.path.isfile(newfn):
        newfn = newfn.replace('.fits', '.0.fits')

    # Write fits file output
    hdulist.writeto(newfn)


if __name__ == "__main__":
    if len(sys.argv) != 4 or any([x == "--help" for x in sys.argv]):
        sys.exit("Usage: %s <input> <ku|l> <sigma>" % sys.argv[0])
    fitsProc(sys.argv[1],sys.argv[2],float(sys.argv[3]))
