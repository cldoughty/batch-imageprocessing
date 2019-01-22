#Imports
import os,glob
os.chdir(r'C:\Users\username\GitHubRepository\Micasense\imageprocessing')
import cv2 #openCV
import exiftool
exiftoolPath = None
if os.name == 'nt':
    exiftoolPath = 'C:/exiftool/exiftool(-k).exe' ##Check application name of future versions
with exiftool.ExifTool(exiftoolPath) as exift:
    print('Exiftool works!')
import numpy as np
import matplotlib.pyplot as plt  #%matplotlib inline
import math
from PIL import Image
import micasense.plotutils as plotutils #Micasense utility modules
import micasense.metadata as metadata
import micasense.utils as msutils

##############################################################################
#Part 1

#Set folder paths
CalibrationFolder_preflight = r'C:\Users\username\GitHubRepository\batch-imageprocessing\test_images\images_calibration\preflight'
CalibrationFolder_postflight = r'C:\Users\username\GitHubRepository\batch-imageprocessing\test_images\images_calibration\postflight'
ImagesFolder = r'C:\Users\username\GitHubRepository\batch-imageprocessing\test_images\images_calibration\images_raw'
ReflectanceImagesFolder = r'C:\Users\username\GitHubRepository\batch-imageprocessing\test_images\images_reflectance'

#import Micasense panel reflectance data
panelCalibration = { 
    "Blue": 0.61, 
    "Green": 0.61, 
    "Red": 0.61, 
    "Red edge": 0.60, 
    "NIR": 0.56 
}

##############################################################################
#Calculate Radiance to Reflectance Conversion for Each Band using the Calibration Panel Images
    #Need to perform manually for each band because masked panel area shifts

#PREFLIGHT CALIBRATION IMAGES
##############
#Band 1 (Blue)
#Plotting
imageName = os.path.join(CalibrationFolder_preflight, 'IMG_0002_1.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 510 # upper left column (x coordinate) of panel area
uly = 350 # upper left row (y coordinate) of panel area
lrx = 710 # lower right column (x coordinate) of panel area
lry = 550 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B1 = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B1))

reflectanceImage = radianceImage * radianceToReflectance_B1
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')


##############
#Band 2 (Green)
#Plotting
imageName = os.path.join(CalibrationFolder_preflight,'IMG_0002_2.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 530 # upper left column (x coordinate) of panel area
uly = 340 # upper left row (y coordinate) of panel area
lrx = 730 # lower right column (x coordinate) of panel area
lry = 540 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B2 = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B2))

reflectanceImage = radianceImage * radianceToReflectance_B2
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')


##############
#Band 3 (Red)
#Plotting
imageName = os.path.join(CalibrationFolder_preflight,'IMG_0002_3.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 550 # upper left column (x coordinate) of panel area
uly = 300 # upper left row (y coordinate) of panel area
lrx = 750 # lower right column (x coordinate) of panel area
lry = 500 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B3 = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B3))

reflectanceImage = radianceImage * radianceToReflectance_B3
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')


##############
#Band 4 (NIR)
#Plotting
imageName = os.path.join(CalibrationFolder_preflight,'IMG_0002_4.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 510 # upper left column (x coordinate) of panel area
uly = 330 # upper left row (y coordinate) of panel area
lrx = 710 # lower right column (x coordinate) of panel area
lry = 530 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B4 = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B4))

reflectanceImage = radianceImage * radianceToReflectance_B4
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')


##############
#Band 5 (Red edge)
#Plotting
imageName = os.path.join(CalibrationFolder_preflight,'IMG_0002_5.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 520 # upper left column (x coordinate) of panel area
uly = 320 # upper left row (y coordinate) of panel area
lrx = 720 # lower right column (x coordinate) of panel area
lry = 520 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B5 = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B5))

reflectanceImage = radianceImage * radianceToReflectance_B5
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')


#Check Radiance to Reflectance conversion for each band
print('Blue: {:1.3f}'.format(radianceToReflectance_B1))
print('Green: {:1.3f}'.format(radianceToReflectance_B2))
print('Red: {:1.3f}'.format(radianceToReflectance_B3))
print('NIR: {:1.3f}'.format(radianceToReflectance_B4))
print('Red edge: {:1.3f}'.format(radianceToReflectance_B5))



#POSTFLIGHT
##############################################################################
#Calculate Radiance to Reflectance Conversion for Each Band using the Calibration Panel Images
##############
#Band 1 (Blue)
#Plotting
imageName = os.path.join(CalibrationFolder_postflight,'IMG_0119_1.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 460 # upper left column (x coordinate) of panel area
uly = 550 # upper left row (y coordinate) of panel area
lrx = 600 # lower right column (x coordinate) of panel area
lry = 700 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B1_post = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B1_post))

reflectanceImage = radianceImage * radianceToReflectance_B1_post
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')


##############
#Band 2 (Green)
#Plotting
imageName = os.path.join(CalibrationFolder_postflight,'IMG_0119_2.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 470 # upper left column (x coordinate) of panel area
uly = 540 # upper left row (y coordinate) of panel area
lrx = 610 # lower right column (x coordinate) of panel area
lry = 690 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B2_post = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B2_post))

reflectanceImage = radianceImage * radianceToReflectance_B2_post
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')


##############
#Band 3 (Red)
#Plotting
imageName = os.path.join(CalibrationFolder_postflight,'IMG_0119_3.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 480 # upper left column (x coordinate) of panel area
uly = 520 # upper left row (y coordinate) of panel area
lrx = 620 # lower right column (x coordinate) of panel area
lry = 670 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B3_post = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B3_post))

reflectanceImage = radianceImage * radianceToReflectance_B3_post
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')


##############
#Band 4 (NIR)
#Plotting
imageName = os.path.join(CalibrationFolder_postflight,'IMG_0119_4.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 460 # upper left column (x coordinate) of panel area
uly = 530 # upper left row (y coordinate) of panel area
lrx = 600 # lower right column (x coordinate) of panel area
lry = 680 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B4_post = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B4_post))

reflectanceImage = radianceImage * radianceToReflectance_B4_post
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')


##############
#Band 5 (Red edge)
#Plotting
imageName = os.path.join(CalibrationFolder_postflight,'IMG_0119_5.tif')
imageRaw=plt.imread(imageName).T  # Read raw image DN values - 16 bit tif only
plt.imshow(imageRaw.T, cmap='gray')
plotutils.colormap('viridis'); # Optional: pick a color map: 'gray, viridis, plasma, inferno, magma, nipy_spectral'
fig = plotutils.plotwithcolorbar(imageRaw.T, title='Raw image values with colorbar')

#Image metadata
meta = metadata.Metadata(imageName, exiftoolPath=exiftoolPath)
bandName = meta.get_item('XMP:BandName')

#Converting raw images to Radiance
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw.T)
plotutils.plotwithcolorbar(V,'Vignette Factor')
plotutils.plotwithcolorbar(R,'Row Gradient Factor')
plotutils.plotwithcolorbar(V*R,'Combined Corrections')
plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values')
plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance')

#Mask to panel and calculate radiance
markedImg = radianceImage.copy()
ulx = 470 # upper left column (x coordinate) of panel area
uly = 520 # upper left row (y coordinate) of panel area
lrx = 610 # lower right column (x coordinate) of panel area
lry = 670 # lower right row (y coordinate) of panel area
cv2.rectangle(markedImg,(ulx,uly),(lrx,lry),(0,255,0),3)
panelRegion = radianceImage[uly:lry, ulx:lrx]
plotutils.plotwithcolorbar(markedImg, 'Panel region in radiance image')

meanRadiance = panelRegion.mean()
print('Mean Radiance in panel region: {:1.3f} W/m^2/nm/sr'.format(meanRadiance))
panelReflectance = panelCalibration[bandName]
radianceToReflectance_B5_post = panelReflectance / meanRadiance
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance_B5_post))

reflectanceImage = radianceImage * radianceToReflectance_B5_post
plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image')

#Check Radiance to Reflectance conversion for each band
print('Blue: {:1.3f}'.format(radianceToReflectance_B1_post))
print('Green: {:1.3f}'.format(radianceToReflectance_B2_post))
print('Red: {:1.3f}'.format(radianceToReflectance_B3_post))
print('NIR: {:1.3f}'.format(radianceToReflectance_B4_post))
print('Red edge: {:1.3f}'.format(radianceToReflectance_B5_post))

#################################################################
#AVG Pre and Post Flight Calibration
#Check Radiance to Reflectance conversion for each band
radianceToReflectance_B1_avg = (radianceToReflectance_B1 + radianceToReflectance_B1_post)/2
radianceToReflectance_B2_avg = (radianceToReflectance_B2 + radianceToReflectance_B2_post)/2
radianceToReflectance_B3_avg = (radianceToReflectance_B3 + radianceToReflectance_B3_post)/2
radianceToReflectance_B4_avg = (radianceToReflectance_B4 + radianceToReflectance_B4_post)/2
radianceToReflectance_B5_avg = (radianceToReflectance_B5 + radianceToReflectance_B5_post)/2

##############################################################################
##############################################################################
#Part 2

#Write function to read band
def get_band(image):
    meta = metadata.Metadata(image, exiftoolPath=exiftoolPath)
    band = meta.get_item('XMP:BandName')
    return band

#Begin loop to process raw images to reflectance
for image in os.listdir(ImagesFolder):
#Ignore all but TIF
    if os.path.splitext(image)[-1] == ".tif":
#Read images and get metadata
        imagepath = os.path.join(ImagesFolder, image)
        band = get_band(imagepath)
        meta = metadata.Metadata(imagepath, exiftoolPath=exiftoolPath)
        ImageRaw=plt.imread(imagepath)
#Convert DN to Radiance
        flightRadianceImage, _, _, _ = msutils.raw_image_to_radiance(meta, ImageRaw)
        #plotutils.plotwithcolorbar(flightRadianceImage, 'Radiance Image')
#Convert Radiance to Reflectance
        if band == "Blue":
            flightReflectanceImage = flightRadianceImage * radianceToReflectance_B1_avg
        elif band == "Green":
            flightReflectanceImage = flightRadianceImage * radianceToReflectance_B2_avg
        elif band == "Red":
            flightReflectanceImage = flightRadianceImage * radianceToReflectance_B3_avg
        elif band == "NIR":
            flightReflectanceImage = flightRadianceImage * radianceToReflectance_B4_avg
        elif band == "Red edge":
            flightReflectanceImage = flightRadianceImage * radianceToReflectance_B5_avg
        else:
            print("error")
#Export TIFF
        if not os.path.exists(ReflectanceImagesFolder):
            os.makedirs(ReflectanceImagesFolder)
        outfile = os.path.join(ReflectanceImagesFolder, image)
        im = Image.fromarray(flightReflectanceImage)
        im.save(outfile)
        #End loop

#############################################################################  
#############################################################################
#Part 3
#Transfer metadata
#Pathways must not have spaces
#Copy the following to the command prompt

#exiftool -tagsFromFile C:\Users\username\GitHubRepository\batch-imageprocessing\test_images\images_calibration\images_raw\%f.tif -file:all -iptc:all -exif:all -xmp -Composite:all C:\Users\username\GitHubRepository\batch-imageprocessing\test_images\images_reflectance -overwrite_original
