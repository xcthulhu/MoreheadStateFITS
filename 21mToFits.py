

import numpy as num
from pyfits import Column, new_table
import pyfits
import math
#Determine RGB values from Greyscale pixel
class Color(object):
     def __init__(self, r, g, b):
         self.r = r
         self.g = g
         self.b = b

     def rgb(self):
         return "rgb(%d, %d, %d)" % (self.r, self.g, self.b)

     def red(self):
         return self.r
        
     def green(self):
         return self.g
        
     def blue(self):
         return self.b  

     def lerp(self, score, color):
         return Color(
            self.interp(score, self.r, color.r),
            self.interp(score, self.g, color.g),
            self.interp(score, self.b, color.b))

     def interp(self, score, x, y):
         return int(x + score * (y - x))

     @staticmethod
     def get_color(score):
         score = score/10.0
         magic = 0.5
         if score < magic:
             return RED.lerp(score / magic, YELLOW)
         else:
             return YELLOW.lerp((score - magic) / (1 - magic), GREEN)

RED    = Color(255, 0, 0)
YELLOW = Color(255, 255, 0)
GREEN  = Color(0, 255, 0)
#**************************************************************************




Band=133.33 #Band is set by default to Ku-Band

RA = []
Dec = []
LST = []
Voltage = []

filenames=[]


## GUI stuff (in progress)

from Tkinter import *
import tkFileDialog
win=Tk()
win.title('21mToFits')

l3 = Label(win, text="Conversion Factor")
l3.grid(row=1, column=1)
b3 = Button(win,text="Open")
b4 = Button(win,text="Save") 

b3.grid(row=6, column=3)
b4.grid(row=7, column=3)

conv = DoubleVar()#conversion factor
conv.set(1.0)#= 1.0 #is 1 by default
en = Entry(win,textvariable=conv)

en.grid(row=3, column=1)


options=[('Ku-Band',1),('L-Band',2),('S-Band',3),('C-Band',4)]
var = IntVar()
row=6
for text, value in options:
    Radiobutton(win, text=text, value=value, variable=var).grid(row=row, column=1)
    row+=1
var.set(1)


l2 = Label(win, text="Selected Files")
l2.grid(row=4, column=1)


lb = Listbox(win, height=3)
lb.grid(row=5, column=1)
sb = Scrollbar(win,orient=VERTICAL)
sb.grid(row=5, column=2)
sb.configure(command=lb.yview)
lb.configure(yscrollcommand=sb.set)
    

def but3() :
    infile=tkFileDialog.askopenfilename()
    lb.insert(END,infile)
    filenames.append(infile)
    print conv.get()

def but4() :

    if (var.get()==1):# if Ku-Band is selected
        Band=133.33

    if (var.get()==2):# if Ku-Band is selected
        Band=6.8966

    #print Band
    
    a=0
    while a<len(filenames):#go through all selected files
    
        file = open(filenames[a], "r")



        ##  We don't want the table headers in the data.
        firstrow = file.readline()
      
        for row in file.readlines():#go through all lines of the file

            column = row.split()
            #Check if RA and Dec already exist
            b=0
            if a is not 0:#only if there is already data in lists
                isThere=0
                while b<len(RA):
                        
                    if RA[b]==(float(column[0])-1)and Dec[b]==(float(column[1])-1):
                        Voltage[b]=Voltage[b]+(float(column[3]))#add up the Voltage
                        isThere=1
                            
                    b=b+1
                if isThere==0:
                    RA.append(float(column[0])-1)
                    Dec.append(float(column[1])-1)
                    LST.append(float(column[2]))
                    Voltage.append(float(column[3]))

            
            else:   
                RA.append(float(column[0])-1)
                Dec.append(float(column[1])-1)
                LST.append(float(column[2]))
                Voltage.append(float(column[3]))
            
                    
       # print len(RA)        
        a=a+1
 
    ##  Convert our data arrays to numpy arrays for pyFits
    numRA = num.array(RA)
    numDec = num.array(Dec)
    numLST = num.array(LST)
    numVoltage = num.array(Voltage)

    ##  Create the fits table columns from our numpy arrays
    colRA = Column(name="RA",format='1E', array=numRA)
    colDec = Column(name="Dec", format='1E', array=numDec)
    colLST = Column(name="LST", format='1E', array=numLST)
    colVoltage = Column(name="Voltage", format='1E', array=numVoltage)

    ##  Create table
    tbhdu = new_table([colRA, colDec, colLST, colVoltage])


    
    ## Centerpoint for Taurus A
    CenterRA=83.633212   
    CenterDec=22.01447222

    ##Centerpoint for Virgo A
    #CenterRA=187.7059304
    #CenterDec=12.3911231 

    ##Centerpoint for Cas A
    #CenterRA=350.85000000
    #CenterDec=58.81500000

    ##Centerpoint for HB21
    #CenterRA=311.25
    #CenterDec=50.58333333

    ##Centerpoint for moon
    #CenterRA=246
    #CenterDec=-26


    ##Centerpoint for Cas A
    #CenterRA=350
    #CenterDec=58



    ##print centerpoint
   # print float(int((CenterRA+0.0005)*1000))/1000 # round to 3 decimals 
   # print float(int((CenterDec+0.0005)*1000))/1000


    numRAmax=0  # highest RA value
    numDecmax=0 # highest Dec value


    ##calculate pixels
    j=0
    while 1:
        numRA[j]=((abs(numRA[j]-CenterRA)*Band))# use 133.33 for Ku-Band 6.8966 for L-Band
        numDec[j]=((abs(numDec[j]-CenterDec)*Band))# use 133.33 for Ku-Band
    #15.88235369 factor for beam width and pixel size
        #print numRA[j]
        #print numDec[j]

        if numDec[j]>numDecmax:
            numDecmax=numDec[j]
        if numRA[j]>numRAmax:
            numRAmax=numRA[j]
    
        j=j+1
        if j==numRA.size:
            break

    ## Adjust file size (in pixels) according to data
    
    sizeX=4096
    sizeY=4096


    if numDecmax>2048 or numRAmax>2048:
        print "Values too big"
    elif numDecmax>1024 or numRAmax>1024:
        sizeX=2048
        sizeY=2048
    elif numDecmax>512 or numRAmax>512:
        sizeX=1024
        sizeY=1024
    elif numDecmax>256 or numRAmax>256:
        sizeX=512
        sizeY=512
    elif numDecmax>128 or numRAmax>128:
        sizeX=256
        sizeY=256
    else :
        sizeX=128
        sizeY=128

    n = num.zeros((sizeX,sizeY),num.int32)
    hdu = pyfits.PrimaryHDU(n)
    hdulist = pyfits.HDUList([hdu])
    scidata=hdulist[0].data


    ## Put data in table
    j=0
    while 1:
        numVoltage[j]=numVoltage[j]*conv.get()#convert Voltage into Janski
        F=Color
        print F.get_color(numVoltage[j]).rgb()#print rgb of each pixel
        print F.get_color(numVoltage[j]).red()
        print F.get_color(numVoltage[j]).green()
        print F.get_color(numVoltage[j]).blue()
        
        scidata[numDec[j],numRA[j]]=numVoltage[j]
        j=j+1
        if j==numRA.size:
            break
    
    hdu.header.update('naxis',2,'Two dimensional image')
    hdu.header.update('naxis1', sizeX,'Width of image')
    hdu.header.update('naxis2', sizeY,'Heigth of image')



    ## Define fits header
    prihdr = hdulist[0].header
    prihdr.update('crval1', CenterRA,'Reference longitude')
    prihdr.update('crval2', CenterDec,'Reference latitude')
    prihdr.update('radesys', 'FK5     ','Coordinate system ')
    prihdr.update('equinox', 2000.0,'Epoch of the equinox')
    prihdr.update('ctype1', 'RA---TAN','Coordinates -- projection')
    prihdr.update('ctype2', 'DEC--TAN','Coordinates -- projection')
    prihdr.update('crpix1', sizeX,'X reference pixel')
    prihdr.update('crpix2', sizeY,'Y reference pixel')
    prihdr.update('cdelt1', -0.0075,'X scale')
    prihdr.update('cdelt2', 0.0075,'Y scale')
    #prihdr.update('cdelt1', -4.7222219999999997E-4,'X scale')
    #prihdr.update('cdelt2', 4.7222219999999997E-4,'Y scale')
    #prihdr.update('institut','Morehead State University','observing institution')
    hdu.verify('fix')

    hdulist.append(tbhdu)

    #Make sure that filename contains ending .fits, if not, add it
    outputfile=tkFileDialog.asksaveasfilename()
    if ".fits" not in outputfile:
        outputfile=outputfile+ ".fits"
        
    hdulist.writeto(outputfile)
    print CenterRA
    print CenterDec

b3.configure(command=but3)
b4.configure(command=but4)


### End of GUI stuff



## Make a list of files to convert into FITS

win.mainloop()


    


















    
