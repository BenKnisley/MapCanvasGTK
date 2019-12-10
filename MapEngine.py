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

import dataLoader


class MapEngine:
    def __init__(self):
        self._WGS84 = pyproj.Proj("EPSG:4326") ## Keep a ref WGS84
        self._proj = pyproj.Proj("EPSG:4326") ## Default to WGS84

        self._scale = 1 ## Default to 1.0

        #! Figure this out
        self._coord = (40.0, -82.0) ## rep for
        self._POI = self.geo2proj(self._coord) ## rep for projection

        self._size = (500,500) ## Default to 500px x 500px

        ## Test data points
        self.points = [(0.0, 0.0), (0.1,0.1), (-0.2,0.2), (0.8,-0.5)]
        #self.points = [(40.205833, -83.613889), (39.305833, -83.713889), (39.405833, -83.613889)]
        #self.points = dataLoader.getData()


    def setPOI(self, newPOI):
        self._POI = newPOI

    def getPOI(self):
        return self._POI


    def setScale(self, newScale):
        self._scale = newScale

    def getScale(self):
        return self._scale


    def getCenterPoint(self):
        x = int(self._size[0]/2)
        y = int(self._size[1]/2)
        return (x, y)


    def setSize(self, newSize): # size tuple (x, y)
        self._size = newSize

    def getSize(self):
        return self._size


    def geo2proj(self, geoPoint): ## geoPoint tuple (lat, lon)
        """ """
        None

    def proj2geo(self, projPoint): ## projPoint tuple (x, y)
        """ """
        None

    def proj2pix(self, projPoint):
        """ """
        None

    def pix2proj(self, pixPoint):
        """ """
        None

    def geo2pix(self, geoPoint):
        """ """
        None

    def pix2geo(self, pixPoint):
        """ """
        None




    def drawMapOnCanvas(self, cr):
        """
        Implements draw slot
        - Draw a test circle in middle of widget
        """
        ## Set color to 95% black
        cr.set_source_rgb(0.05, 0.05, 0.05)
        ## Draw rectangle over entire widget
        cr.rectangle( 0,0, self._size[0], self._size[1] )
        ## Fill rectangle
        cr.fill()

        ## Set color to red
        cr.set_source_rgb(1, 0, 0)

        for p in self.points:
            #p2 = self.geo2pix(p)
            ## Draw small circle in center of screen
            cr.arc(p[0], p[1], 2, 0, 6.2830)
            #print cr.clip_extents()
            ## Fill circle
            cr.fill()
