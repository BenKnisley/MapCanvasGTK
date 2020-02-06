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


## Import MapEngine, and VectorLayer
from MapEngine import MapEngine, VectorLayer


class ToolController(GObject.GObject):
    """
    Class to receive signals & abstract higher level functions.
    """
    def __init__(self, map):
        """ """
        GObject.GObject.__init__(self)

        self.map = map

        ## Define public mouse button trackers
        self.leftHeld = False
        self.LDragPOS = (None, None)

        self.midHeld = False
        self.MDragPOS = (None, None)

        self.rightHeld = False
        self.RDragPOS = (None, None)

    def buttonPress(self, caller, click):
        if click.button == 1: ## Left click
            self.leftHeld = True
            self.LDragPOS = (click.x, click.y)

        elif click.button == 2: ## Middle click
            self.midHeld = True
            self.MDragPOS = (click.x, click.y)

        else: ## Right click
            self.rightHeld = True
            self.RDragPOS = (click.x, click.y)

    def buttonRelease(self, caller, click):
        if click.button == 1: ## Left click
            self.leftHeld = False
            self.LDragPOS = (None, None)

            #print( self.map.getPOI() )

        elif click.button == 2: ## Middle click
            self.midHeld = False
            self.MDragPOS = (None, None)

        else: ## Right click
            self.rightHeld = False
            self.RDragPOS = (None, None)

            ##

    def mouseDrag(self, caller, move):
        if self.leftHeld:
            ## Unpack Points
            cenX, cenY = self.map.get_canvas_center()
            orgnX, orgnY = self.LDragPOS

            ## Calulate new pixel point from drag distance
            newPixPoint = ( (cenX + (orgnX - move.x)), (cenY + -(orgnY - move.y)) )

            ## Calulate new map POI
            newProjPoint = self.map.pix2proj(newPixPoint)
            self.map.set_POI(newProjPoint)

            ## Set drag orgin point
            self.LDragPOS = (move.x, move.y)

            ## Call redraw
            caller.callRedraw(self)

        if self.midHeld:
            pass

        if self.rightHeld:
            pass

    def scroll(self, caller, scroll):
        """ """
        if int(scroll.direction) == 0:
            self.map.set_scale( self.map.get_scale() * 1.1 )
        else:
            self.map.set_scale( self.map.get_scale() / 1.1 )

        caller.callRedraw(self)

class MapView(Gtk.DrawingArea, MapEngine.MapEngine):
    """ """
    def __init__(self):
        """ """
        ## Implement inheritance from Gtk.Window & Gtk.GObject
        Gtk.DrawingArea.__init__(self)
        GObject.GObject.__init__(self)
        MapEngine.MapEngine.__init__(self)

        ## Create ToolController Object
        self.tools = ToolController(self)

        ## Add capability to detect mouse events
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add_events(Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.add_events(Gdk.EventMask.BUTTON2_MOTION_MASK)
        self.add_events(Gdk.EventMask.BUTTON3_MOTION_MASK)
        self.add_events(Gdk.EventMask.SCROLL_MASK)

        ## Connect Stuff
        self.connect("configure_event", self.startup)
        self.connect("scroll-event", self.tools.scroll)
        self.connect("button-press-event", self.tools.buttonPress)
        self.connect("button-release-event", self.tools.buttonRelease)
        self.connect("motion-notify-event", self.tools.mouseDrag)
        self.connect("draw", self.draw)

    def startup(self, caller, data):
        pass

    def callRedraw(self, caller):
        """ Causes canvas to redraw self """
        self.queue_draw()

    def draw(self, caller, cr):
        """ """
        ## Call on map engine to draw map on canvas
        self.set_size((self.get_allocated_width(), self.get_allocated_height()))
        self.draw_map(cr)
        #exit()
