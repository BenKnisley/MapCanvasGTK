#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: January 1, 2020
"""

class CairoMapPainter:

    def drawPoint(self, cr, point, style):
        """ """
        R, G, B = style.pointcolor
        rad = style.pointradius

        cr.set_source_rgb(R, G, B)
        cr.arc(point[0], point[1], rad, 0, 6.2830)
        cr.fill()

    def drawLine(self, cr, line, style):
        """ """
        R, G, B = style.linecolor
        W = style.linewidth

        cr.set_source_rgb(R, G, B)
        cr.set_line_width(W)

        initPnt = line[0]
        cr.move_to( initPnt[0], initPnt[1] )

        for point in line:
            cr.line_to( point[0], point[1] )

        cr.stroke()

    def drawPolygon(self, cr, polygon, style):
        """ """
        R, G, B = style.polyColor
        cr.set_source_rgb(R, G, B)

        for subpoly in polygon:
            initPnt = subpoly[0]
            cr.move_to( initPnt[0], initPnt[1] )

            for point in subpoly:
                cr.line_to( point[0], point[1] )
        cr.fill()


        R, G, B = style.polyLineColor
        W = style.polyLineWidth

        ## Draw line outline
        cr.set_source_rgb(R, G, B)
        cr.set_line_width(W)

        for subpoly in polygon:
            initPnt = subpoly[0]
            cr.move_to( initPnt[0], initPnt[1] )

            for point in subpoly:
                cr.line_to( point[0], point[1] )
            cr.stroke()