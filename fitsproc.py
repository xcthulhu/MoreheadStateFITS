import sys, os, pyfits, csv
import numpy as np

def fitsproc(fn):
    # Load the tsv file
    fp = open(fn, 'rb')
    data = csv.reader(fp, delimiter='\t')

    # Thow away header data
    data.next()

    # Extract RA, DEC, and Voltage from the raw data
    # We use a list comprehension
    ra,dec,voltage = np.transpose(
        np.array([np.array([float(row[0]),
                            float(row[1]),
                            float(row[3])]) 
                      for row in data]))

    # The following is taken from the Dutch PyFITS tutorial here:
    # http://www.astro.rug.nl/~belikov/VO2010/Werkcolleges/W5/Pyfits_tutorial.pdf
    # Make a FITS HDU from the data series
    c1=pyfits.Column(name='RA', format='D', array=ra)
    c2=pyfits.Column(name='DEC', format='D', array=dec)
    c3=pyfits.Column(name='V', format='D', array=dec)
    cs=pyfits.ColDefs([c1,c2,c3])
    table_hdu=pyfits.new_table(cs)
    hdu=pyfits.PrimaryHDU()
    hdulist=pyfits.HDUList([hdu])
    hdulist.append(table_hdu)
    hdulist.verify()

    # Get new datafile name from argument
    ext = os.path.splitext(fn)[1]
    newfn = fn.replace(ext,'.fits')

    # Write fits file output
    hdulist.writeto(newfn)
    fp.close()

if __name__ == "__main__":
    if len(argv) != 3 or any([x == "--help" for x in argv]):
        sys.exit("Usage: %s <input.xls> <output.fits>" % sys.argv[0])
    fitsproc(sys.argv[1])
