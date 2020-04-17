#!/usr/bin/env python3
"""
Project: MapViewer
Title: Main Executable
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 December, 2019
Function: UI entry point for user
"""
## Import PyGtk Modules
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject

## Import MapWidget
from MapCanvasGTK import MapCanvas
from MapEngine import CairoPainter as renderer
from MapEngine import VectorLayer


class MapViewerApplication(Gtk.Application):
    """ The root GTK object for the application. Opens MainWindow. """

    def __init__(self):
        """ Opens MainWindow and connects signals & slots. """
        ## Set ID and flags, initialize Gtk Application parent.
        app_id="apps.test.MapViewer"
        flags=Gio.ApplicationFlags.FLAGS_NONE
        Gtk.Application.__init__(self, application_id=app_id, flags=flags)

        ## Initialize self object.
        self.window = MainWindow()

        ## Connect self activate signal, with self on_activate slot
        self.connect("activate", self._on_activate)

    def _on_activate(self, caller):
        self.window.show_all()
        self.add_window(self.window)


class MainWindow(Gtk.Window):
    """ The main application window, hosts the MapView widget """
    def __init__(self):
        """ Defines window properties, & adds child widgets. """
        ## Initialize parents: Gtk.Window & Gtk.GObject
        Gtk.Window.__init__(self)
        GObject.GObject.__init__(self)

        ## Set own window properties
        self.resize(1700, 900)
        self.set_title("Map Viewer")
        self.set_border_width(0)

        ## Create widgets
        self.map = MapCanvas()

        #self.map.set_projection("EPSG:4326")
        #self.map.set_projection("EPSG:3857")
        #self.map.set_projection("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
        self.map.set_projection("EPSG:32023")
        self.map.set_location(40.0,-83.0)
        self.map.set_scale(1000)
        self.map.set_background_color('black')

        ## Create map layers


        #WorldCountries = VectorLayer.from_shapefile("./data/WorldCountries.shp")
        #self.map.add_layer(WorldCountries)
        #self.map.add_layer(WorldCountries)

        OhioCounties = VectorLayer.from_shapefile("/home/ben/Geography/Data/Ohio Counties/OhioCounties.shp")
        self.map.add_layer(OhioCounties)
        #self.map.add_layer(ohio_roads)

        #ohio_roads = VectorLayer.from_shapefile("./data/ohio_roads.shp")
        #self.map.add_layer(ohio_roads)

        #[f.set_color('red') for f in polys if f['name'] == "Highland"]
        #[f.set_line_width(0.1) for f in polys]


        #self.map.add_layer(counties)

        ## Create layout, add MapView, and add layout to window
        self.layout = Gtk.VBox()
        self.layout.pack_start(self.map, True, True, 0)
        self.add(self.layout)



## Main function. Run application, if not imported.
if __name__ == "__main__":
    ## Create app instance and run it
    app = MapViewerApplication()
    app.run()
