#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 December, 2019

Project: MapViewer
Title: Main Executable
Function: UI entry point for user
"""
## Import PyGtk Modules
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject

## Import MapWidget
from MapView import MapView


class MyApplication(Gtk.Application):
    """ """
    def __init__(self):
        ## Initialize Gtk Application parent, set ID and flags
        Gtk.Application.__init__(
            self,
            application_id="apps.test.GeoCanvasWindow",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        ## Connect self activate signal, with self on_activate slot
        self.connect("activate", self.on_activate)


    def on_activate(self, data=None):
        ## Initialize window as mainWindow object
        window = mainWindow()

        ## Make all widgets on mainWindow visible
        window.show_all()

        ## Add window to self application
        self.add_window(window)



class mainWindow(Gtk.Window):
    def __init__(self):
        ## Initialize parents: Gtk.Window & Gtk.GObject
        Gtk.Window.__init__(self)
        GObject.GObject.__init__(self)

        ## Set self window properties
        self.resize(1200, 800)
        self.set_title("Map Viewer")
        #self.set_border_width(10)

        ## Create widgets
        self.map = MapView()



        ## Create, pack, and add layout to window
        self.layout = Gtk.VBox()
        
        self.layout.pack_start(self.map, True, True, 0)

        self.add(self.layout)



## Main function. Run application, if not imported.
if __name__ == "__main__":
    ## Create app instance and run it
    app = MyApplication()
    app.run()
