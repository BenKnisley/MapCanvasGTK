#!/usr/bin/env python3
"""
Project: MapViewer
Title: MapView Widget
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 December, 2019
Function: A Gtk Widget that provides a map.
"""
## Import PyGtk Modules
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject

## Import PyProj
import pyproj
import numpy as np
import dataLoader


class MapEngine:
    """
    """
    def __init__(self):
        ## Keep a ref WGS84
        self._WGS84 = pyproj.Proj("EPSG:4326")

        ## Variable projection
        #self._proj = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84') ## Default to WGS84
        self._proj = pyproj.Proj("EPSG:32023") ## Default to WGS84

        ## Set default scale
        self._scale = 0.0005 ## Default to 1.0
        #self._scale = 100 ## Default to 1.0


        #! Figure this shit out
        self._coord = (40.0, -83.0) ## rep for
        self._POI = self.geo2proj(self._coord) ## rep for projection

        ## Set default size
        self._size = (500,500) ## Default to 500px x 500px

        ## Test data points
        #self.points = [(40.0, -82.0)]
        #self.points = [(0.0, 0.0), (0.1,0.1), (-0.2,0.2), (0.8,-0.5)]
        #self.points = [(40.205833, -83.613889), (39.305833, -83.713889), (39.405833, -83.613889)]
        self.points = dataLoader.getData()
        self.points = [(40.0, -83.0)] + self.points

    def getProjection(self):
        return self._proj

    def setProjection(self, newProjection):
        None

    def setPOI(self, newPOI):
        """ """
        self._POI = newPOI

    def getPOI(self):
        return self._POI

    def setScale(self, newScale):
        self._scale = newScale

    def getScale(self):
        return self._scale

    def setSize(self, newSize): # size tuple (x, y)
        self._size = newSize

    def getSize(self):
        return self._size

    def getCenterPoint(self):
        x = int(self._size[0]/2)
        y = int(self._size[1]/2)
        return (x, y)


    def geo2proj(self, geoPoint): ## geoPoint tuple (lat, lon)
        """
        """
        if isinstance(geoPoint, list):
            lat = [coord[0] for coord in geoPoint]
            lon = [coord[1] for coord in geoPoint]
            x, y = pyproj.transform(self._WGS84, self._proj, lat, lon)
            projPoint = list( zip(x,y) )
        else:
            lat, lon = geoPoint
            x, y = pyproj.transform(self._WGS84, self._proj, lat, lon)
            projPoint = (x, y)

        return projPoint

    def proj2geo(self, projPoint): ## projPoint tuple (x, y)
        """ """
        x, y = projPoint
        lon, lat = pyproj.transform(self._WGS84, self._proj, x, y)
        geoPoint = (lat, lon)
        return geoPoint

    def proj2pix(self, projPoint):
        """ """
        ## Unpack points
        focusX, focusY = self._POI
        centerX, centerY = self.getCenterPoint()

        if isinstance(projPoint, list):
            ## Break list of projPoints in x and y list
            x = [coord[0] for coord in projPoint]
            y = [coord[1] for coord in projPoint]

            ## Convert lists of points to numpy arrays
            x = np.array(x)
            y = np.array(y)

            ## Do math logic on all points
            pixelX = ((x - focusX) * self._scale) + centerX
            pixelY = -((y - focusY) * self._scale) + centerY

            pixPoint = list( zip(pixelX, pixelY) )

        else:
            projX, projY = projPoint
            ##
            pixelX = ((projX - focusX) * self._scale) + centerX
            pixelY = -((projY - focusY) * self._scale) + centerY
            pixPoint = (pixelX, pixelY)

        return pixPoint

    def pix2proj(self, pixPoint):
        """ """
        None

    def geo2pix(self, geoPoint):
        """ """
        projPoint = self.geo2proj(geoPoint)
        pixPoint = self.proj2pix(projPoint)
        return pixPoint

    def pix2geo(self, pixPoint):
        """ """
        None

    def drawMapOnCanvas(self, cr):
        """
        Implements draw slot
        - Draw a test circle in middle of widget
        """
        ## Draw background
        cr.set_source_rgb(0.05, 0.05, 0.05) ## Set color to 95% black
        cr.rectangle( 0,0, self._size[0], self._size[1] ) ## Draw rectangle over entire widget
        cr.fill() ## Fill rectangle

        cr.set_source_rgb(1, 0, 0)  ## Set color to red

        points = self.geo2pix(self.points)

        for p in points:
            ## Draw small circle in center of screen
            cr.arc(p[0], p[1], 1, 0, 6.2830)
            #print cr.clip_extents()
            ## Fill circle
            cr.fill()
