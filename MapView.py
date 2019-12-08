#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 December, 2019

Project: MapViewer
Title: MapView Widget
Function: A Gtk Widget that provides a map.
"""


class MapView(Gtk.DrawingArea):
    def __init__(self):
        ## Implement inheritance from Gtk.Window & Gtk.GObject
        Gtk.DrawingArea.__init__(self)
        GObject.GObject.__init__(self)
    
