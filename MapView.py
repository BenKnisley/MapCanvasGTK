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

## Import MapEngine
import MapEngine


class ToolController:
    def __init__(self):
        GObject.GObject.__init__(self)


class MapView(Gtk.DrawingArea):
    def __init__(self):
        ## Implement inheritance from Gtk.Window & Gtk.GObject
        Gtk.DrawingArea.__init__(self)
        GObject.GObject.__init__(self)

        ## Add capability to detect mouse events
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add_events(Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.add_events(Gdk.EventMask.SCROLL_MASK)


        ## Create MapEngine Object
        self.map = MapEngine.MapEngine()

        ## Connect Stuff
        self.connect("draw", self.draw)


    def callRedraw(self, caller):
        """ Causes canvas to redraw self """
        self.queue_draw()


    def draw(self, caller, cr):
        """ """
        ## Call on map engine to draw map on canvas
        self.map.setSize((self.get_allocated_width(), self.get_allocated_height()))
        self.map.drawMapOnCanvas(cr)
