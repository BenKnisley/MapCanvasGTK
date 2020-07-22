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

import time



class UI_Tool(GObject.GObject):
    def __init__(self):
        self.parent = None

        self.draw_list = []

    def activate(self, parent):
        self.parent = parent
        #self.parent.connect("left-click", self.left_click)
        #elf.parent.connect("right-click", self.select_at_click)
        self.parent.connect("double-click", self.select_at_click)
        self.parent.connect("middle-click", self.middle_click)
        self.parent.connect("left-drag-update", self.left_drag)
        self.parent.connect("scroll-up", self.scroll_up)
        self.parent.connect("scroll-down", self.scroll_down)

    def left_drag(self, caller, x_change, y_change):
        """ """
        ## Calculate new pixel point from drag distance
        temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.parent.width, self.parent.height)
        cr = cairo.Context(temp_surface)

        cr.save()
        cr.translate(int(x_change), int(y_change))
        cr.set_source_surface(self.parent.rendered_map)
        cr.paint()
        cr.restore()

        center_x, center_y = self.parent.get_canvas_center()
        projx, projy = self.parent.pix2proj((center_x - x_change), (center_y + y_change))
        self.parent.set_proj_coordinate(projx, projy)

        self.parent.rendered_map = temp_surface
        ## Call redraw
        self.parent.call_redraw(self)
        self.parent.map_updated = True

    def scroll_up(self, caller):
        ##
        temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.parent.width, self.parent.height)
        cr = cairo.Context(temp_surface)

        cr.save()

        x_w = -((self.parent.width * 1.1) - self.parent.width) / 2
        x_h = -((self.parent.height * 1.1) - self.parent.height) / 2


        cr.translate(x_w, x_h)
        cr.scale(1.1, 1.1)

        cr.set_source_surface(self.parent.rendered_map)
        cr.paint()
        cr.restore()

        self.parent.rendered_map = temp_surface
        ## Call redraw
        self.parent.call_redraw(self)

        self.parent.map_updated = True
        self.parent.set_scale( self.parent.get_scale() / 1.1 )

        ##
        self.parent.call_redraw(self)

    def scroll_down(self, caller):
        temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.parent.width, self.parent.height)
        cr = cairo.Context(temp_surface)

        cr.save()

        x_w = -((self.parent.width / 1.1) - self.parent.width) / 2
        x_h = -((self.parent.height / 1.1) - self.parent.height) / 2


        cr.translate(int(x_w), int(x_h))
        cr.scale(1/1.1, 1/1.1)

        cr.set_source_surface(self.parent.rendered_map)
        cr.paint()
        cr.restore()

        self.parent.rendered_map = temp_surface
        ## Call redraw
        self.parent.call_redraw(self)

        self.parent.map_updated = True
        self.parent.set_scale( self.parent.get_scale() * 1.1 )
        
        ##
        self.parent.call_redraw(self)
    
    def middle_click(self, caller, x,y):
        self.draw_list = []
        self.parent.call_redraw(self)


    def select_at_click(self, caller, x, y):
        """ """
        proj_x, proj_y = self.parent.pix2proj(x, self.parent.height - y)

        layer = self.parent.get_layer(0)
        selected_features = layer.point_select(proj_x, proj_y)

        for feature in selected_features:
            if feature not in self.draw_list:
                self.draw_list.append(feature)

        ## Redraw widget with selected features highlighted
        self.parent.call_redraw(self)


    def draw(self, cr):
        """ """
        for f in self.draw_list:
            f.draw(self.parent.get_layer(0), self.parent.renderer, cr, color_over_ride='yellow')


class _ToolController(GObject.GObject):
    """
    Class to receive signals & abstract higher level functions.
    """
    def __init__(self, map):
        """ """
        GObject.GObject.__init__(self)

        self.map = map

        ## Define public mouse button trackers
        self.click_time = 0
        self.left_active = False
        self.left_init_position = (None, None)
        self.left_updated_position = (None, None)
        
        self.middle_active = False
        self.middle_init_position = (None, None)
        self.middle_updated_position = (None, None)

        self.right_active = False
        self.right_init_position = (None, None)
        self.right_updated_position = (None, None)

    def buttonPress(self, caller, click):
        if click.button == 1: ## Left click
            self.left_active = True
            self.left_init_position = (click.x, click.y)

        elif click.button == 2: ## Middle click
            self.middle_active = True
            self.middle_init_position = (click.x, click.y)

        else: ## Right click
            self.right_active = True
            self.right_init_position = (click.x, click.y)

    def buttonRelease(self, caller, click):
        if click.button == 1: ## Left click
            ## Do stuff, send signals
            if (time.time() - self.click_time) < 0.25:
                self.map.emit('double-click', int(click.x), int(click.y))
            elif (click.x, click.y) == self.left_init_position:
                self.map.emit('left-click', int(click.x), int(click.y))
            else:
                self.map.emit('left-drag-end', int(click.x), int(click.y))

            ## Reset trackers
            self.click_time = time.time()
            self.left_active = False
            self.left_init_position = (None, None)
            self.left_updated_position = (None, None)

        elif click.button == 2: ## Middle click
            ## Do Stuff
            if (click.x, click.y) == self.middle_init_position:
                self.map.emit('middle-click', int(click.x), int(click.y))
            else:
                self.map.emit('middle-drag-end', int(click.x), int(click.y))
            ## Reset
            self.middle_active = False
            self.middle_init_position = (None, None)
            self.middle_updated_position = (None, None)

        else: ## Right click
            ## Do Stuff
            if (click.x, click.y) == self.right_init_position:
                self.map.emit('right-click', int(click.x), int(click.y))
            else:
                self.map.emit('right-drag-end', int(click.x), int(click.y))
            ## Reset
            self.right_active = False
            self.right_init_position = (None, None)
            self.right_updated_position = (None, None)

    def mouseDrag(self, caller, move):
        if self.left_active:

            if self.left_updated_position == (None, None):
                self.map.emit('left-drag-start', int(move.x), int(move.y))
                self.left_updated_position = self.left_init_position
            

            init_x, init_y = self.left_updated_position

            self.map.emit('left-drag-update', move.x-init_x, move.y-init_y)

            ## Set drag origin point
            self.left_updated_position = (move.x, move.y)


        if self.middle_active:
            if self.middle_updated_position == (None, None):
                self.map.emit('middle-drag-start', int(move.x), int(move.y))
                self.middle_updated_position = self.middle_init_position
            

            init_x, init_y = self.middle_updated_position

            self.map.emit('middle-drag-update', move.x-init_x, move.y-init_y)

            ## Set drag origin point
            self.middle_updated_position = (move.x, move.y)

        if self.right_active:
            if self.right_updated_position == (None, None):
                self.map.emit('right-drag-start', int(move.x), int(move.y))
                self.right_updated_position = self.right_init_position
            

            init_x, init_y = self.right_updated_position

            self.map.emit('right-drag-update', move.x-init_x, move.y-init_y)

            ## Set drag origin point
            self.right_updated_position = (move.x, move.y)

    def scroll(self, caller, scroll):
        """ """
        if int(scroll.direction) == 0:
            self.map.emit("scroll-up")
        else:
            self.map.emit("scroll-down")




class MapCanvas(Gtk.DrawingArea, PyMapKit.Map):
    """ """
    def __init__(self):
        """ """
        ## Implement inheritance from GObject, DrawingArea, and PyMapKit.Map
        GObject.GObject.__init__(self)
        Gtk.DrawingArea.__init__(self)
        PyMapKit.Map.__init__(self)

        self.set_background_color('black')

        ## Create custom signals
        GObject.signal_new("layer-added", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (str,)) 

        GObject.signal_new("scroll-up", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, ()) 
        GObject.signal_new("scroll-down", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, ()) 

        GObject.signal_new("left-click", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int)) 
        GObject.signal_new("double-click", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int)) 
        GObject.signal_new("left-drag-start", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("left-drag-update", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("left-drag-end", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 

        GObject.signal_new("middle-click", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int)) 
        GObject.signal_new("middle-drag-start", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("middle-drag-update", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("middle-drag-end", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 

        GObject.signal_new("right-click", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int)) 
        GObject.signal_new("right-drag-start", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("right-drag-update", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("right-drag-end", MapCanvas, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 


        ## Background rendering thread variables
        self.rendered_map = None
        self.render_thread = None
        self.is_rendering = False
        self.map_updated = True

        ## Create ToolController Object
        self.tools = _ToolController(self)

        
        self.tool = UI_Tool()
        self.tool.activate(self)
        

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

        self.tool.draw(cr)
        
        ## Render map in another thread whenever GTK feels like it
        self.call_map_render(self)
