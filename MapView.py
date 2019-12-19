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

import time

## Import MapEngine
import MapEngine


class ToolController(GObject.GObject):
    def __init__(self, map):
        GObject.GObject.__init__(self)

        self.map = map


        ## Define mouse button trackers
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
        elif click.button == 2: ## Middle click
            self.midHeld = False
            self.MDragPOS = (None, None)
        else: ## Right click
            self.rightHeld = False
            self.RDragPOS = (None, None)


    def mouseDrag(self, caller, move):
        if self.leftHeld:
            print("Left Drag")


        if self.midHeld:
            ## Unpack Points
            cenX, cenY = self.map.getCenterPoint()
            orgnX, orgnY = self.MDragPOS

            ## Calulate new pixel point from drag distance
            newPixPoint = ( (cenX + (orgnX - move.x)), (cenY + -(orgnY - move.y)) )

            ## Calulate new map POI
            newProjPoint = self.map.pix2proj(newPixPoint)
            self.map.setPOI(newProjPoint)

            ## Set drag orgin point
            self.MDragPOS = (move.x, move.y)

            ## Call redraw
            caller.callRedraw(self)


        if self.rightHeld:
            #print("Right Drag")
            None


    def scroll(self, caller, scroll):
        """ """
        if int(scroll.direction) == 0:
            self.map.zoomIn()
            caller.callRedraw(self)

        else:
            self.map.zoomOut()
            caller.callRedraw(self)



class MapView(Gtk.DrawingArea):
    def __init__(self):
        ## Implement inheritance from Gtk.Window & Gtk.GObject
        Gtk.DrawingArea.__init__(self)
        GObject.GObject.__init__(self)

        ## Add capability to detect mouse events
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add_events(Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.add_events(Gdk.EventMask.BUTTON2_MOTION_MASK)
        self.add_events(Gdk.EventMask.BUTTON3_MOTION_MASK)
        self.add_events(Gdk.EventMask.SCROLL_MASK)


        ## Create MapEngine Object
        self.map = MapEngine.MapEngine()

        ## Create ToolController Object
        self.tools = ToolController(self.map)

        ## Connect Stuff

        self.connect("configure_event", self.hello)
        self.connect("scroll-event", self.tools.scroll)
        self.connect("button-press-event", self.tools.buttonPress)
        self.connect("button-release-event", self.tools.buttonRelease)
        self.connect("motion-notify-event", self.tools.mouseDrag)

        self.connect("draw", self.draw)

    def hello(self, *args):
        None

    def callRedraw(self, caller):
        """ Causes canvas to redraw self """
        self.queue_draw()


    def draw(self, caller, cr):
        """ """
        ## Call on map engine to draw map on canvas
        self.map.setSize((self.get_allocated_width(), self.get_allocated_height()))
        self.map.paintCanvas(cr)
