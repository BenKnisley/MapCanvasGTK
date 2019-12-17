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



"""
These functions will get moved into the MapLayer Object soon enough.
"""
def drawPoint(cr, point):
    """ """
    cr.arc(point[0], point[1], 1, 0, 6.2830)
    cr.fill()

def drawLine(cr, line):
    """ """
    cr.set_source_rgb(0, 0, 1)
    cr.set_line_width(1)

    initPnt = line[0]
    cr.move_to( initPnt[0], initPnt[1] )

    for point in line:
        cr.line_to( point[0], point[1] )

    cr.stroke()


def drawPolygon(cr, polygon):
    """ """
    None



class MapEngine:
    """
    """
    def __init__(self):
        ## Keep a ref WGS84
        self._WGS84 = pyproj.Proj("EPSG:4326")

        ## Variable projection
        #self._proj = pyproj.Proj("EPSG:4326", preserve_units=True)
        self._proj = pyproj.Proj("+proj=longlat +a=6378140 +b=6356750 +no_defs")
        #self._proj = pyproj.Proj("EPSG:32023")
        #self._proj = pyproj.Proj("+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6378140 +b=6356750 +units=m +no_defs")
        #self._proj = pyproj.Proj("+proj=aeqd +lat_0=90 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")
        #self._proj = pyproj.Proj("+proj=aeqd +lat_0=40 +lon_0=-83 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")

        ## Set default scale
        self._scale = 5.0 ## Default to 1.0

        #! Figure this shit out
        self._coord = (-83.0, 40.0) ## rep for
        self._POI = self.geo2proj(self._coord) ## rep for projection

        ## Set default size
        self._size = (500,500) ## Default to 500px x 500px

        ## Test data points
        #self.points = [(40.0, -82.0)]
        #self.points = [(0.0, 0.0), (0.1,0.1), (-0.2,0.2), (0.8,-0.5)]
        #self.points = [(40.205833, -83.613889), (39.305833, -83.713889), (39.405833, -83.613889)]

        ## To be exported to MapLayer in future
        self.type, features = dataLoader.getLineFeatures1()

        self.features = []
        for geoLine in features:
            projLine = self.geo2proj(geoLine)
            self.features.append(projLine)



        #self.points = dataLoader.getData()
        #self.points = [(-83.0, 40.0)] + self.points





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
        self._scale += (self._scale * 0.1)

    def zoomOut(self):
        self._scale -= (self._scale * 0.1)

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
            #!!! switched 1, and 0
            lat = [coord[1] for coord in geoPoint]
            lon = [coord[0] for coord in geoPoint]
            x, y = pyproj.transform(self._WGS84, self._proj, lat, lon)
            #x,y = y,x
            projPoint = list( zip(x,y) )
        else:
            lon, lat = geoPoint
            x, y = pyproj.transform(self._WGS84, self._proj, lat, lon)
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
            pixelX = ((x - focusX) * self._scale) + centerX
            pixelY = -((y - focusY) * self._scale) + centerY

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
        projX = ((pixX - centerX) / self._scale) + focusX
        projY = ((pixY - centerY) / self._scale) + focusY

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



    def drawMapOnCanvas(self, cr):
        """
        Implements draw slot
        - Draw a test circle in middle of widget
        """
        """
        ## Draw background
        cr.set_source_rgb(0.05, 0.05, 0.05) ## Set color to 95% black
        cr.rectangle( 0,0, self._size[0], self._size[1] ) ## Draw rectangle over entire widget
        cr.fill() ## Fill rectangle

        cr.set_source_rgb(1, 0, 0)  ## Set color to red

        points = self.geo2pix(self.points)

        for p in points:
            drawPoint(cr, p)
        """

        ## Draw background
        cr.set_source_rgb(0.05, 0.05, 0.05) ## Set color to 95% black
        cr.rectangle( 0,0, self._size[0], self._size[1] ) ## Draw rectangle over entire widget
        cr.fill() ## Fill rectangle

        if self.type == "line":

            for projLine in self.features:
                pixLine = self.proj2pix(projLine)
                drawLine(cr, pixLine)
