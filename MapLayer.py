#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: December 31, 2019
"""



"""
These functions will get moved into a Cairo MapPainter Object soon enough.
"""
def drawPoint(cr, point, style):
    """ """
    R, G, B = style.pointcolor
    rad = style.pointradius

    cr.set_source_rgb(R, G, B)
    cr.arc(point[0], point[1], rad, 0, 6.2830)
    cr.fill()

def drawLine(cr, line, style):
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

def drawPolygon(cr, polygon, style):
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





"""
Rename this. Buiild it up to be more usable.
"""
class mapStyle:
    def __init__(self):
        self.pointcolor = (0.61, 0.13, 0.15)
        self.pointradius = 2

        self.linecolor = (0,0,1)
        self.linewidth = 1

        self.polyColor = (0.31, 0.34, 0.68)
        self.polyLineColor = (1.0, 1.0, 1.0)
        self.polyLineWidth = 0.25



class MapLayer:
    def __init__(self, mapEng, geotype, inputdata):

        ##
        self.mapEng = mapEng
        self.geotype = geotype
        self.rawdata = inputdata

        self.features = []
        self.styles = []

        self.projectData()

        x = mapStyle()
        self.setStyle(x)

    def projectData(self):
        self.features = [] ## Clear existing features
        if self.geotype == 'point':
            self.features = self.mapEng.geo2proj( self.rawdata )

        elif self.geotype == 'line':
            for line in self.rawdata:
                self.features.append( self.mapEng.geo2proj(line) )

        else:# self.geotype == polygon:
            for polygon in self.rawdata:
                projPoly = []
                for subpoly in polygon:
                    projPoly.append( self.mapEng.geo2proj(subpoly) )
                self.features.append(projPoly)

    def setStyle(self, style):
        for _ in self.features:

            if len(self.styles) % 2 == 0:
                x = mapStyle()
                x.polyColor = (1,1,0)
                self.styles.append(x)
            else:
                self.styles.append(style)

    def draw(self, cr):
        if self.geotype == 'point':
            pixPoints = self.mapEng.proj2pix(self.features)
            for point, style in zip(pixPoints, self.styles):
                drawPoint(cr, point, style)

        elif self.geotype == 'line':
            for projLine, style in zip(self.features, self.styles):
                pixLine = self.mapEng.proj2pix(projLine)
                drawLine(cr, pixLine, style)

        else: # self.geotype == polygon:
            for projFeature, style in zip(self.features, self.styles):
                pixPoly = []
                for subPoly in projFeature:
                    pixsubPoly = self.mapEng.proj2pix(subPoly)
                    pixPoly.append(pixsubPoly)

                drawPolygon(cr, pixPoly, style)
