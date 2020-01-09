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
from MapView import MapView


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
        self.map = MapView()

        ## Create layout, add MapView, and add layout to window
        self.layout = Gtk.VBox()
        self.layout.pack_start(self.map, True, True, 0)
        self.add(self.layout)



## Main function. Run application, if not imported.
if __name__ == "__main__":
    ## Create app instance and run it
    app = MapViewerApplication()
    app.run()
