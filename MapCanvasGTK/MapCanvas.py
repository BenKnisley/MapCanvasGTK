#!/usr/bin/env python3
"""
Project: PyGTK Map Canvas
Title: MapCanvas & UITool Classes
Function: Provides GTK widget for displaying a map.
Author: Ben Knisley [benknisley@gmail.com]
Created: 8 December, 2019
"""
## Import Python built-ins
import threading
import time

## Import PyGtk modules
import gi
import cairo
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject, GLib

## Import PyMapKit module
import PyMapKit

class UITool(GObject.GObject):
    """
    A Tool for MapCanvas providing click to pan, scroll to zoom functionality.
    """

    def __init__(self):
        self.parent = None

    def activate(self, parent):
        self.parent = parent
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
       
        ## Call redraw of 
        self.parent.call_redraw(self)
        
        ## Call for map to be rerendered
        self.parent.call_rerender(self)

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

        self.parent.set_scale( self.parent.get_scale() / 1.1 )
        self.parent.call_rerender(self)

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

        self.parent.call_rerender(self)
        self.parent.set_scale( self.parent.get_scale() * 1.1 )
        
        ##
        self.parent.call_redraw(self)
    
    def middle_click(self, caller, x,y):
        self.selected = []
        self.parent.call_redraw(self)

    def draw(self, cr):
        """ """
        pass


class _SignalManager(GObject.GObject):
    """
    Class to receive and send signals on the behalf of MapCanvas to abstract higher 
    level functions.
    """

    def __init__(self, parent):
        """ """
        GObject.GObject.__init__(self)

        self.map = parent

        ## Add capability to detect mouse events
        self.map.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.map.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.map.add_events(Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.map.add_events(Gdk.EventMask.BUTTON2_MOTION_MASK)
        self.map.add_events(Gdk.EventMask.BUTTON3_MOTION_MASK)
        self.map.add_events(Gdk.EventMask.SCROLL_MASK)

        ## Connect Stuff
        self.map.connect("scroll-event", self.scroll)
        self.map.connect("button-press-event", self.buttonPress)
        self.map.connect("button-release-event", self.buttonRelease)
        self.map.connect("motion-notify-event", self.mouseDrag)


        ## Create custom signals
        GObject.signal_new("layer-added", self.map, GObject.SIGNAL_RUN_FIRST, None, (object,)) 
        GObject.signal_new("layer-removed", self.map, GObject.SIGNAL_RUN_FIRST, None, (object,)) 
        
         
        GObject.signal_new("location-changed", self.map, GObject.SIGNAL_RUN_FIRST, None, (float, float, float, float)) 

        GObject.signal_new("scroll-up", self.map, GObject.SIGNAL_RUN_FIRST, None, ()) 
        GObject.signal_new("scroll-down", self.map, GObject.SIGNAL_RUN_FIRST, None, ()) 

        GObject.signal_new("left-click", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int)) 
        GObject.signal_new("double-click", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int)) 
        GObject.signal_new("left-drag-start", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("left-drag-update", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("left-drag-end", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 

        GObject.signal_new("middle-click", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int)) 
        GObject.signal_new("middle-drag-start", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("middle-drag-update", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("middle-drag-end", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 

        GObject.signal_new("right-click", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int)) 
        GObject.signal_new("right-drag-start", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("right-drag-update", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 
        GObject.signal_new("right-drag-end", self.map, GObject.SIGNAL_RUN_FIRST, None, (int, int,)) 


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
    """
    A widget that renders a map.
    """

    def __init__(self, add_UITool=True):
        """ """
        ## Implement inheritance from GObject, DrawingArea, and PyMapKit.Map
        GObject.GObject.__init__(self)
        Gtk.DrawingArea.__init__(self)
        PyMapKit.Map.__init__(self)

        ## Create _SignalManager Object to handle map signals for us
        self.signal_man = _SignalManager(self)
        
        ## Allow map to have keyboard focus
        self.set_can_focus(True)

        ## Connect basic widget signals
        self.connect("configure_event", self.refresh_window)
        self.connect("size-allocate", self.refresh_window)
        self.connect("draw", self.draw)
        
        ## Set map attributes
        self.set_background_color('black')

        ## Add a list to hold tools
        self.tools = []

        ## UITool flag is true, add a UItool
        if add_UITool:
            self.add_tool(UITool())

        ## Create background rendering thread variables
        self.rendered_map = None
        self.render_thread = None
        self.is_rendering = False
        self.map_updated = True

        ##
        self.active_layer_index = None
    
    """ Tool Functions """

    def add_tool(self, new_tool):
        new_tool.activate(self)
        self.tools.append(new_tool)
    
    def remove_tool(self, tool):
        tool.deactivate()
        self.tools.remove(tool)

    def set_proj_coordinate(self, new_proj_x, new_proj_y):
        super().set_proj_coordinate(new_proj_x, new_proj_y)
        self.emit("location-changed", *self.proj2geo(new_proj_x, new_proj_y), new_proj_x, new_proj_y)



    """ Overriding and extending Map methods """
    def add_layer(self, new_map_layer, index=-1):
        """ """
        #@ Extend PyMapKit.add_layer
        super().add_layer(new_map_layer, index)

        ## 
        self.emit("layer-added", new_map_layer)
        self.call_rerender(self)
        self.call_redraw(self)

    def remove_layer(self, remove_layer):
        """ """
        #@ Extend PyMapKit.remove_layer
        super().remove_layer(remove_layer)

        ## 
        self.emit("layer-removed", remove_layer)
        self.call_rerender(self)
        self.call_redraw(self)

    """ Slots Methods """
    def refresh_window(self, caller, data):
        """ """
        ## When widget is first created: queue rendering
        self.call_rerender(self)
        self.call_redraw(self)

    """ Map Rendering functions """
    
    def call_rerender(self, caller):
        """ Hard ask map to rerender """
        self.map_updated = True
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
    
    """ Widget Drawing functions """

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

        for tool in self.tools:
            tool.draw(cr)
        
        ## Draw map again
        self.call_redraw(self)
