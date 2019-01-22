#!/usr/bin/env python
# coding: utf-8
"""
RedEdge Image Class

    An Image is a single file taken by a RedEdge camera representing one
    band of multispectral information

Copyright 2017 MicaSense, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import cv2
import math
import numpy as np

import matplotlib.pyplot as plt
import micasense.plotutils as plotutils
import micasense.metadata as metadata

class Image(object):
    """
    An Image is a single file taken by a RedEdge camera representing one
    band of multispectral information
    """
    def __init__(self, image_path):
        if not os.path.isfile(image_path):
            raise IOError("Provided path is not a file: {}".format(image_path))
        self.path = image_path
        self.meta = metadata.Metadata(self.path)

        if not self.meta.supports_radiometric_calibration():
            raise ValueError('Library requires images taken with camera firmware v2.1.0 or later. ' +
            'Upgrade your camera firmware to use this library.')

        self.utc_time = self.meta.utc_time()
        self.latitude, self.longitude, self.altitude = self.meta.position()
        self.dls_present = self.meta.dls_present()
        self.dls_yaw, self.dls_pitch, self.dls_roll = self.meta.dls_pose()
        self.dls_irradiance = self.meta.dls_irradiance()
        self.capture_id = self.meta.capture_id()
        self.flight_id = self.meta.flight_id()
        self.band_name = self.meta.band_name()
        self.band_index = self.meta.band_index()
        self.black_level = self.meta.black_level()
        self.radiometric_cal = self.meta.radiometric_cal()
        self.exposure_time = self.meta.exposure()
        self.gain = self.meta.gain()
        self.bits_per_pixel = self.meta.bits_per_pixel()
        self.vignette_center = self.meta.vignette_center()
        self.vignette_polynomial = self.meta.vignette_polynomial()
        self.distortion_parameters = self.meta.distortion_parameters()
        self.principal_point = self.meta.principal_point()
        self.focal_plane_resolution_px_per_mm = self.meta.focal_plane_resolution_px_per_mm()
        self.focal_length = self.meta.focal_length_mm()
        self.center_wavelength = self.meta.center_wavelength()
        self.bandwidth = self.meta.bandwidth()

        if self.bits_per_pixel != 16:
            NotImplemented("Unsupported pixel bit depth: {} bits".format(self.bits_per_pixel))

        self.__raw_image = None # pure raw pixels
        self.__intensity_image = None # black level and gain-exposure/radiometric compensated
        self.__radiance_image = None # calibrated to radiance
        self.__reflectance_image = None # calibrated to reflectance (0-1)
        self.__reflectance_irradiance = None
        self.__undistorted_source = None # can be any of raw, intensity, radiance
        self.__undistorted_image = None # current undistorted image, depdining on source

    def __lt__(self, other):
        return self.band_index < other.band_index
    
    def __gt__(self, other):
        return self.band_index > other.band_index
    
    def __eq__(self, other):
        return (self.band_index == other.band_index) and \
               (self.capture_id == other.capture_id)

    def __ne__(self, other):
        return (self.band_index != other.band_index) or \
               (self.capture_id != other.capture_id)

    def raw(self):
        ''' Lazy load the raw image once neecessary '''
        if self.__raw_image is None:
            try:
                self.__raw_image = cv2.imread(self.path,-1)
            except IOError:
                print("Could not open image at path {}".format(self.path))
                raise
        return self.__raw_image
            
    def clear_image_data(self):
        ''' clear all computed images to reduce memory overhead '''
        self.__raw_image = None
        self.__intensity_image = None
        self.__radiance_image = None
        self.__reflectance_image = None
        self.__reflectance_irradiance = None
        self.__undistorted_source = None
        self.__undistorted_image = None

    def size(self):
        width, height = self.meta.image_size()
        return width, height

    def reflectance(self, irradiance=None, force_recompute=False):
        ''' Lazy-compute and return a reflectance image provided an irradiance reference '''
        if self.__reflectance_image is not None \
            and force_recompute == False \
            and (self.__reflectance_irradiance == irradiance or irradiance == None):
            return self.__reflectance_image
        if irradiance is None:
            raise RuntimeError("Provide a band-specific spectral irradiance to compute reflectance")
        self.__reflectance_irradiance = irradiance
        self.__reflectance_image = self.radiance() * math.pi / irradiance
        return self.__reflectance_image

    def intensity(self, force_recompute=False):
        ''' Lazy=computes and returns the intensity image after black level,
            vignette, and row correction applied. 
            Intensity is in units of DN*Seconds without a radiance correction '''
        if self.__intensity_image is not None and force_recompute == False:
            return self.__intensity_image

        # get image dimensions
        image_raw = np.copy(self.raw()).T

        #  get radiometric calibration factors
        _, a2, a3 = self.radiometric_cal[0], self.radiometric_cal[1], self.radiometric_cal[2]

        # apply image correction methods to raw image
        V, x, y = self.vignette()
        R = 1.0 / (1.0 + a2 * y / self.exposure_time - a3 * y)
        L = V * R * (image_raw - self.black_level)
        L[L < 0] = 0
        max_raw_dn = float(2**self.bits_per_pixel)
        intensity_image = L.astype(float)/(self.gain * self.exposure_time * max_raw_dn)

        self.__intensity_image = intensity_image.T
        return self.__intensity_image

    def radiance(self, force_recompute=False):
        ''' Lazy=computes and returns the radiance image after all radiometric
        corrections have been applied '''
        if self.__radiance_image is not None and force_recompute == False:
            return self.__radiance_image

        # get image dimensions
        image_raw = np.copy(self.raw()).T

        #  get radiometric calibration factors
        a1, a2, a3 = self.radiometric_cal[0], self.radiometric_cal[1], self.radiometric_cal[2]

        # apply image correction methods to raw image
        V, x, y = self.vignette()
        R = 1.0 / (1.0 + a2 * y / self.exposure_time - a3 * y)
        L = V * R * (image_raw - self.black_level)
        L[L < 0] = 0
        max_raw_dn = float(2**self.bits_per_pixel)
        radiance_image = L.astype(float)/(self.gain * self.exposure_time)*a1/max_raw_dn

        self.__radiance_image = radiance_image.T
        return self.__radiance_image

    def vignette(self):
        ''' Get a numpy array which defines the value to multiply each pixel by to correct
        for optical vignetting effects.
        Note: this array is transposed from normal image orientation and comes as part
        of a three-tuple, the other parts of which are also used by the radiance method.
        '''
        # get vignette center
        vignette_center_x, vignette_center_y = self.vignette_center

        # get a copy of the vignette polynomial because we want to modify it here
        v_poly_list = list(self.vignette_polynomial)

        # reverse list and append 1., so that we can call with numpy polyval
        v_poly_list.reverse()
        v_poly_list.append(1.)
        v_polynomial = np.array(v_poly_list)

        # perform vignette correction
        # get coordinate grid across image, seem swapped because of transposed vignette
        x_dim, y_dim = self.raw().shape[1], self.raw().shape[0]
        x, y = np.meshgrid(np.arange(x_dim), np.arange(y_dim))

        #meshgrid returns transposed arrays
        x = x.T
        y = y.T

        # compute matrix of distances from image center
        r = np.hypot((x-vignette_center_x), (y-vignette_center_y))

        # compute the vignette polynomial for each distance - we divide by the polynomial so that the
        # corrected image is image_corrected = image_original * vignetteCorrection
        vignette = 1./np.polyval(v_polynomial, r)
        return vignette, x, y
    
    def plottable_vignette(self):
        return self.vignette()[0].T
    
    def cv2_distortion_coeff(self):
        #dist_coeffs = np.array(k[0],k[1],p[0],p[1],k[2]])
        return np.array(self.distortion_parameters)[[0, 1, 3, 4, 2]]

    # values in pp are in [mm], rescale to pixels
    def principal_point_px(self):
        center_x = self.principal_point[0] * self.focal_plane_resolution_px_per_mm[0]
        center_y = self.principal_point[1] * self.focal_plane_resolution_px_per_mm[1]
        return (center_x, center_y)

    def cv2_camera_matrix(self):
        center_x, center_y = self.principal_point_px()

        # set up camera matrix for cv2
        cam_mat = np.zeros((3, 3))
        cam_mat[0, 0] = self.focal_length * self.focal_plane_resolution_px_per_mm[0]
        cam_mat[1, 1] = self.focal_length * self.focal_plane_resolution_px_per_mm[1]
        cam_mat[2, 2] = 1.0
        cam_mat[0, 2] = center_x
        cam_mat[1, 2] = center_y

        # set up distortion coefficients for cv2
        return cam_mat

    def undistorted(self, image):
        ''' return the undistorted image from input image '''
        # If we have already undistorted the same source, just return that here
        # otherwise, lazy compute the undstorted image
        if self.__undistorted_source is not None and image.data == self.__undistorted_source.data:
            return self.__undistorted_image
        
        self.__undistorted_source = image

        new_cam_mat, _ = cv2.getOptimalNewCameraMatrix(self.cv2_camera_matrix(), 
                                                       self.cv2_distortion_coeff(),
                                                       self.size(), 
                                                       1)
        map1, map2 = cv2.initUndistortRectifyMap(self.cv2_camera_matrix(),
                                                self.cv2_distortion_coeff(),
                                                np.eye(3),
                                                new_cam_mat,
                                                self.size(),
                                                cv2.CV_32F) # cv2.CV_32F for 32 bit floats
        # compute the undistorted 16 bit image
        self.__undistorted_image = cv2.remap(image, map1, map2, cv2.INTER_LINEAR)
        return self.__undistorted_image

    def plot_raw(self, title=None, figsize=None):
        ''' Create a single plot of the raw image '''
        if title is None:
            title = '{} Band {} Raw DN'.format(self.band_name, self.band_index)
        return plotutils.plotwithcolorbar(self.raw(), title=title, figsize=figsize)

    def plot_intensity(self, title=None, figsize=None):
        ''' Create a single plot of the image converted to uncalibrated intensity '''
        if title is None:
            title = '{} Band {} Intensity (DN*sec)'.format(self.band_name, self.band_index)
        return plotutils.plotwithcolorbar(self.intensity(), title=title, figsize=figsize)


    def plot_radiance(self, title=None, figsize=None):
        ''' Create a single plot of the image converted to radiance '''
        if title is None:
            title = '{} Band {} Radiance'.format(self.band_name, self.band_index)
        return plotutils.plotwithcolorbar(self.radiance(), title=title, figsize=figsize)

    def plot_vignette(self, title=None, figsize=None):
        ''' Create a single plot of the vignette '''
        if title is None:
            title = '{} Band {} Vignette'.format(self.band_name, self.band_index)
        return plotutils.plotwithcolorbar(self.plottable_vignette(), title=title, figsize=figsize)

    def plot_undistorted_radiance(self, title=None, figsize=None):
        ''' Create a single plot of the undistorted radiance '''
        if title is None:
            title = '{} Band {} Undistorted Radiance'.format(self.band_name, self.band_index)
        return plotutils.plotwithcolorbar(self.undistorted(self.radiance()), title=title, figsize=figsize)

    def plot_all(self, figsize=(13,10)):
        plots = [self.raw(), self.plottable_vignette(), self.radiance(), self.undistorted(self.radiance())]
        plot_types = ['Raw', 'Vignette', 'Radiance', 'Undistorted Radiance']
        titles = ['{} Band {} {}'.format(str(self.band_name), str(self.band_index), tpe)
                 for tpe in plot_types]
        plotutils.subplotwithcolorbar(2, 2, plots, titles, figsize=figsize)