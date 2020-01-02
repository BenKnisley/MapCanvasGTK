#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: December 31, 2019
"""


class _FeatureStyle:
    def __init__(self):
        self.pointcolor = (0.61, 0.13, 0.15)
        self.pointradius = 2

        self.linecolor = (0,0,1)
        self.linewidth = 1

        self.polyColor = (0.31, 0.34, 0.68)
        self.polyLineColor = (0.0, 1.0, 0.5)
        self.polyLineWidth = 0.5


class VectorLayer:
    def __init__(self, host_map_engine, geotype, inputdata):

        ##
        self._map_engine = host_map_engine
        self.geotype = geotype
        self.rawdata = inputdata

        self.features = []
        self.attributes = []
        self.styles = []

        self.projectData()

        ## Set Defalt map style to each feature
        new_style = _FeatureStyle()
        for _ in self.features:
            self.styles.append(new_style)

    def projectData(self):
        self.features = [] ## Clear existing features
        if self.geotype == 'point':
            self.features = self._map_engine.geo2proj( self.rawdata )

        elif self.geotype == 'line':
            for line in self.rawdata:
                self.features.append( self._map_engine.geo2proj(line) )

        else:# self.geotype == polygon:
            for polygon in self.rawdata:
                projPoly = []
                for subpoly in polygon:
                    projPoly.append( self._map_engine.geo2proj(subpoly) )
                self.features.append(projPoly)

    def setStyle(self, index, style):
        """ """
        None

    def draw(self, cr):
        if self.geotype == 'point':
            pixPoints = self._map_engine.proj2pix(self.features)
            for point, style in zip(pixPoints, self.styles):
                self._map_engine._map_painter.drawPoint(cr, point, style)

        elif self.geotype == 'line':
            for projLine, style in zip(self.features, self.styles):
                pixLine = self._map_engine.proj2pix(projLine)
                self._map_engine._map_painter.drawLine(cr, pixLine, style)

        else: # self.geotype == polygon:
            for projFeature, style in zip(self.features, self.styles):
                pixPoly = []
                for subPoly in projFeature:
                    pixsubPoly = self._map_engine.proj2pix(subPoly)
                    pixPoly.append(pixsubPoly)

                self._map_engine._map_painter.drawPolygon(cr, pixPoly, style)
