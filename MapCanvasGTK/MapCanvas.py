#!/usr/bin/env python3
"""
Project: MapViewer
Title: MapView Widget
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 December, 2019
Function: A Gtk Widget that provides a map.
"""
## Import built-ins
import threading

## Import PyGtk modules
import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject, GLib

## Import PyMapKit module
import PyMapKit




class UI_Tool(GObject.GObject):
    def __init__(self):
        pass



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
            self.map.call_redraw(self)

        else: ## Right click
            self.rightHeld = False
            self.RDragPOS = (None, None)

            ##

    def mouseDrag(self, caller, move):
        if self.leftHeld:
            ## Unpack Points
            cenX, cenY = self.map.get_canvas_center()
            orgnX, orgnY = self.LDragPOS

            ## Calculate new pixel point from drag distance
            newPixPoint = ( (cenX + (orgnX - move.x)), (cenY + -(orgnY - move.y)) )

            self.map.emit('left-drag', (orgnX - move.x), (orgnY - move.y))

            temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.map.width, self.map.height)
            cr = cairo.Context(temp_surface)

            cr.save()
            cr.translate(int(move.x - orgnX), int(move.y - orgnY))
            cr.set_source_surface(self.map.rendered_map)
            cr.paint()
            cr.restore()

            self.map.rendered_map = temp_surface
            ## Call redraw
            caller.call_redraw(self)

            ## Calulate new map POI

            projx, projy = self.map.pix2proj(newPixPoint[0], newPixPoint[1])
            self.map.set_proj_coordinate(projx, projy)
            self.map.map_updated = True

            ## Set drag orgin point
            self.LDragPOS = (move.x, move.y)

        if self.midHeld:
            pass

        if self.rightHeld:
            pass


    def left_drag_slot(self, caller, x, y):
        pass


    def scroll(self, caller, scroll):
        """ """
        if int(scroll.direction) == 0:
            
            ##
            temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.map.width, self.map.height)
            cr = cairo.Context(temp_surface)

            cr.save()

            x_w = -((self.map.width * 1.1) - self.map.width) / 2
            x_h = -((self.map.height * 1.1) - self.map.height) / 2


            cr.translate(x_w, x_h)
            cr.scale(1.1, 1.1)

            cr.set_source_surface(self.map.rendered_map)
            cr.paint()
            cr.restore()

            self.map.rendered_map = temp_surface
            ## Call redraw
            caller.call_redraw(self)

            self.map.map_updated = True
            self.map.set_scale( self.map.get_scale() / 1.1 )
            ##


        else:
            temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.map.width, self.map.height)
            cr = cairo.Context(temp_surface)

            cr.save()

            x_w = -((self.map.width / 1.1) - self.map.width) / 2
            x_h = -((self.map.height / 1.1) - self.map.height) / 2


            cr.translate(int(x_w), int(x_h))
            cr.scale(1/1.1, 1/1.1)

            cr.set_source_surface(self.map.rendered_map)
            cr.paint()
            cr.restore()

            self.map.rendered_map = temp_surface
            ## Call redraw
            caller.call_redraw(self)

            self.map.map_updated = True
            self.map.set_scale( self.map.get_scale() * 1.1 )

        caller.call_redraw(self)

class MapCanvas(Gtk.DrawingArea, PyMapKit.Map):
    """ """
    def __init__(self):
        """ """
        ## Implement inheritance from GObject, DrawingArea, and PyMapKit.Map
        GObject.GObject.__init__(self)
        Gtk.DrawingArea.__init__(self)
        PyMapKit.Map.__init__(self)

        GObject.signal_new("layer-added", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (str,)) ## self.emit('layer-added', "hello")

        GObject.signal_new("left-click", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (str,)) ## self.emit('layer-added', "hello")
        GObject.signal_new("left-drag", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) ## self.emit('layer-added', "hello")

        ## Background rendering thread variables
        self.rendered_map = None
        self.render_thread = None
        self.is_rendering = False
        self.map_updated = True

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
        self.connect("draw", self.draw)
        self.connect("left-drag", self.ping)
        
        self.connect("button-press-event", self.tools.buttonPress)
        self.connect("button-release-event", self.tools.buttonRelease)
        self.connect("motion-notify-event", self.tools.mouseDrag)

    def add_layer(self, new_map_layer, index=-1):
        """ """
        ## Call new_map_layer activate function
        new_map_layer._activate(self)

        ## Add layer to layer_list
        if index == -1:
            self._layer_list.insert(len(self._layer_list), new_map_layer)
        else:
            self._layer_list.insert(index, new_map_layer)
        
        self.map_updated = True
        self.call_redraw(self)

    def ping(self, caller, x, y):
        print("Left Drag", x, y)


    def startup(self, caller, data):
        ## When widget is first created: queue rendering
        self.call_map_render(self)

    def call_map_render(self, caller):
        GObject.idle_add(self.start_render_thread)

    def start_render_thread(self):
        """ Opens render_map in a thread """ 
        if self.map_updated:
            if not self.is_rendering:
                self.render_thread = threading.Thread(target=self.render_map)
                self.render_thread.setDaemon(False)
                self.render_thread.start()

    def render_map(self):
        """ Renders map to self.rendered_map """
        self.map_updated = False
        self.is_rendering = True

        temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.get_allocated_width(), self.get_allocated_height())
        cr = cairo.Context(temp_surface)
        self.render(cr)

        if self.map_updated == False:
            self.rendered_map = temp_surface
        else:
            self.render_map()

        self.map_updated = False
        self.is_rendering = False

        self.call_redraw(self)
    
    def call_redraw(self, caller):
        """ Asks canvas to redraw itself """
        self.queue_draw()

    def draw(self, caller, cr):
        """ """
        ## Set match size matches widget size
        self.set_size(self.get_allocated_width(), self.get_allocated_height())

        self.renderer.draw_background(cr, self._background_color)
        
        ## If
        if self.rendered_map:
            cr.set_source_surface(self.rendered_map)
            cr.paint()
            self.render_thread.join(0)


        
        ## Render map in another thread whenever GTK feels like it
        self.call_map_render(self)
