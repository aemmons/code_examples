#!/usr/bin/env python

#instantDay.py

############################################################
#
# This file must be executed from within project directory.
# Project directory should be setup as follows:
#           <projectDir>
#               <RAWimg>
#               <TIFFimg>
#               <work>
#                   <temp>
#
#   This script will attemp to create such a setup if one
#   does not exist.
#       -RAWimg contains original RAW files
#       -TIFFimg will contain TIFF files after script run
#       -work will contain final image
#       -temp is temporary storage of image files as
#           script creates during runtime.
#
##########################################################

import os
import sys
import subprocess
from subprocess import  call
import PIL
from PIL import Image


#UFRAW flag settings
saturation='.5'
blackPoint='.05'
exposure='.5'
imgWidth=3039
imgHeight=2014


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

#Get list of RAW files
RAWlist = os.listdir('./RAWimg')
RAWlist.sort()

#Process RAW files saving TIFF images to TIFFimg dir

#for RAWfilename in RAWlist:
#    #Execute UFRAW command
#    cmd = "/Applications/ufraw.app/Contents/MacOS/ufraw-batch --wb=auto --out-type=tiff8 --nozip --interpolation=ahd --out-path=./TIFFimg --base-curve=camera --saturation="+saturation+" --black-point="+blackPoint+" --exposure="+exposure+"  ./RAWimg/"+RAWfilename
#    print "Running: "+RAWfilename
#    
#    #subprocess.call(cmd, shell=False)
#    os.system(cmd)




#create empty tmp image using PIL
theIMG = Image.new('RGB',(imgWidth,imgHeight),)


#Process TIFF images
TIFFlist = os.listdir('./TIFFimg')
TIFFlist.sort()
column = 0
sliceWidth=int(imgWidth/len(TIFFlist))

#foreach $tiff in $TIFFimgs
for TIFFfilename in TIFFlist:
    #open $tiff with PIL
    print 'FILENAME: ./TIFFimg/'+TIFFfilename
    tmpIMG = Image.open('./TIFFimg/'+TIFFfilename)
    
    #crop column
    slice = tmpIMG.crop(((column*sliceWidth), 0, (column*sliceWidth)+sliceWidth, imgHeight))
    
    #paste column into tmp image
    theIMG.paste(slice, ((column*sliceWidth),0))
    print "Pasted: "+TIFFfilename
    
    #close $tiff
    
    column += 1
    
    
#save final image to work dir
theIMG.save('work/final.tif')
