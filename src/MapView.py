#!/usr/bin/env python3
"""
Project: MapViewer
Title: MapView Widget
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 December, 2019
Function: A Gtk Widget that provides a map.
"""
## Import PyGtk modules
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject

## Import MapEngine modules
import MapEngine



class _ToolController(GObject.GObject):
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
            self.map.callRedraw(self)

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
            newProjPoint = self.map.pix2proj(newPixPoint[0], newPixPoint[1])
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

class MapCanvas(Gtk.DrawingArea, MapEngine.MapEngine):
    """ """
    def __init__(self):
        """ """
        ## Implement inheritance from GObject, DrawingArea, and MapEngine.
        GObject.GObject.__init__(self)
        Gtk.DrawingArea.__init__(self)
        MapEngine.MapEngine.__init__(self)

        ## Create ToolController Object
        self.tools = _ToolController(self)

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
        ## Set match size matches widget size
        self.set_size((self.get_allocated_width(), self.get_allocated_height()))
        ## Call MapEngine render method on Cario context
        self.render(cr)
