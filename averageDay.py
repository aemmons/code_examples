##############################
#averageDay.py


#!/usr/bin/env python

import os
import sys
import PIL
from PIL import Image
import numpy
import time
import math


imgWidth=3039
imgHeight=2014

R, G, B = 0, 1, 2


#Setup and confirm project workspace
#Check for RAWimg dir, create upon failure
if not os.path.exists('./RAWimg'):
    sys.exit("ERROR: RAWimg directory does not exist.")
    
#Check for TIFFimg dir, create upon failure
if not os.path.exists('./TIFFimg'):
    os.makedirs('./TIFFimg')

#Check for work dir, create upon failure
if not os.path.exists('./work'):
    os.makedirs('./work')

#Check for work/temp dir, create upon failure
if not os.path.exists('./work/temp'):
    os.makedirs('./work/temp')
    

#Arrays to hold total pixel values info
rTot = numpy.zeros(shape=(imgHeight,imgWidth))
gTot= numpy.zeros(shape=(imgHeight,imgWidth))
bTot= numpy.zeros(shape=(imgHeight,imgWidth))

#create empty tmp image using PIL
theIMG = Image.new('RGB',(imgWidth,imgHeight),)


#Process TIFF images
TIFFlist = os.listdir('./TIFFimg')
TIFFlist.sort()
count = len(TIFFlist)
column = 0
sliceWidth=int(imgWidth/count)

#foreach $tiff in $TIFFimgs
for TIFFfilename in TIFFlist:
    #open $tiff with PIL
    print 'FILENAME: ./TIFFimg/'+TIFFfilename
    tmpIMG = Image.open('./TIFFimg/'+TIFFfilename)
    tmpIMG.load()
    
    # split the image into individual bands
    source = tmpIMG.split()

    #load color channels into PIL objects for pixel access
    red = source[R].load()
    green = source[G].load()
    blue = source[B].load()

    print "adding pixels for " + TIFFfilename
    print time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    
    #Loop thru Pixels, adding them. Row by Row.
    for y in range(0, imgHeight):
        #print TIFFfilename + " Adding pixels in row: ", y
        for x in range(0, imgWidth):
            #print "r: ", red[x,y]
            rTot[y,x] += red[x,y]
            #print "g: ", green[x,y]
            gTot[y,x] += green[x,y]
            #print "b: ", blue[x,y]
            bTot[y,x] += blue[x,y]
            
    print "r: ", rTot[0,0]
    print "g: ", gTot[0,0]
    print "b: ", bTot[0,0]


print "Averaging Color Values"

#Average color Channel values
for y in range(0, imgHeight):
    #print "Averaging row: ", y
    for x in range(0, imgWidth):
        red[x,y]= math.floor(rTot[y,x] / count)
        green[x,y]= math.floor(gTot[y,x] / count)
        blue[x,y]= math.floor(bTot[y,x] / count)


theIMG = Image.merge(theIMG.mode,source)
    
#save final image to work dir
theIMG.save('work/final.tif')
