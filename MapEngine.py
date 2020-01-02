#!/usr/bin/env python3
"""
Project: Map Engine
Title: MapEngine
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 December, 2019
Function:
"""
## Import PyProj, and numpy
import pyproj
import numpy as np

## Import MapLayer and style
from VectorLayer import VectorLayer
import CairoMapPainter


class MapEngine:
    """
    """
    def __init__(self, projection, initCoord):
        """ """
        ## Keep a reference WGS84
        self._WGS84 = pyproj.Proj("EPSG:4326")

        ## Variable projection
        self._proj = pyproj.Proj(projection)
        self._scale = 0.01
        self._POI = self.geo2proj(initCoord)

        ## Set default size
        self._size = (500, 500) ## Default to 500px x 500px

        ## Create MapPainter object
        self._map_painter = CairoMapPainter.CairoMapPainter()

        ## Create list to hold layers
        self._layer_list = []

    def addLayer(self, new_map_layer):
        """
        """
        self._layer_list.append(new_map_layer)


    def getProjection(self):
        return self._proj

    def setProjection(self, newProjection):
        None


    def setPOI(self, newPOI):
        """ """
        self._POI = newPOI

    def getPOI(self):
        return self._POI


    def zoomIn(self):
        self._scale -= (self._scale * 0.1)

    def zoomOut(self):
        self._scale += (self._scale * 0.1)


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

        if self._WGS84 == self._proj:
            return geoPoint


        if isinstance(geoPoint, list):
            #!!! switched 1, and 0
            lat = [coord[1] for coord in geoPoint]
            lon = [coord[0] for coord in geoPoint]
            x, y = pyproj.transform(self._WGS84, self._proj, lat, lon)
            #x,y = y,x
            projPoint = list( zip(x,y) )
        else:
            lon, lat = geoPoint
            x, y = pyproj.transform(self._WGS84, self._proj, lat, lon) ## alwaysXy
            #x,y = y,x
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
            pixelX = ((x - focusX) / self._scale) + centerX
            pixelY = -((y - focusY) / self._scale) + centerY

            #pixelX, pixelY = pixelY, pixelX

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
        ## Unpack points
        focusX, focusY = self._POI
        centerX, centerY = self.getCenterPoint()
        pixX, pixY = pixPoint

        ##
        projX = ((pixX - centerX) * self._scale) + focusX
        projY = ((pixY - centerY) * self._scale) + focusY

        ##
        projPoint = (projX, projY)


        ##
        return projPoint

    def geo2pix(self, geoPoint):
        """ """
        projPoint = self.geo2proj(geoPoint)
        pixPoint = self.proj2pix(projPoint)
        return pixPoint

    def pix2geo(self, pixPoint):
        """ """
        projPoint = self.pix2proj(pixPoint)
        geoPoint = self.proj2geo(projPoint)
        return geoPoint



    def paintCanvas(self, cr):
        """
        Implements draw slot
        - Draw a test circle in middle of widget
        """

        ## Draw background
        cr.set_source_rgb(0.05, 0.05, 0.05) ## Set color to 95% black
        cr.rectangle( 0,0, self._size[0], self._size[1] ) ## Draw rectangle over entire widget
        cr.fill() ## Fill rectangle


        for layer in self._layer_list:
            layer.draw(cr)
