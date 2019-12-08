#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 December, 2019

Project: MapViewer
Title: MapView Widget
Function: A Gtk Widget that provides a map.
"""
## Import PyGtk Modules
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject

class MapView(Gtk.DrawingArea):
    def __init__(self):
        ## Implement inheritance from Gtk.Window & Gtk.GObject
        Gtk.DrawingArea.__init__(self)
        GObject.GObject.__init__(self)

        ## Connect Stuff
        self.connect("draw", self.draw)

    def draw(self, caller, cr):
        """
        Implements draw slot
        - Draw a test circle in middle of widget
        """
        ## Set color to 95% black
        cr.set_source_rgb(0.05, 0.05, 0.05)
        ## Draw rectangle over entire widget
        cr.rectangle( 0,0, self.get_allocated_width(), self.get_allocated_height() )
        ## Fill rectangle
        cr.fill()

        ## Set color to red
        cr.set_source_rgb(1, 0, 0)
        ## Draw small circle in center of screen
        cr.arc(self.get_allocation().width/2, self.get_allocation().height/2, 2, 0, 6.2830)
        #print cr.clip_extents()
        ## Fill circle
        cr.fill()
