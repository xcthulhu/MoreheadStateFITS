import xlrd
import sys
import pyfits
import numpy as np

def fitsproc(ifn,ofn):
    wb = xlrd.open_workbook(ifn)
    sh = wb.sheet_by_index(0)
    data = np.array([np.array(sh.row_values(x)) for x in range(sh.nrows)])
    hdu = pyfits.PrimaryHDU(data)
    hdu.writeto(ofn)

if __name__ == "__main__":
    if len(argv) != 3 or any([x == "--help" for x in argv]):
        sys.exit("Usage: %s <input.xls> <output.fits>" % sys.argv[0])
    fitsproc(sys.argv[1],sys.argv[2])
