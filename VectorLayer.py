#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: December 31, 2019
"""

## Import OGR
from osgeo import ogr





def _get_geom_points(geom):
    """
    Given a OGR geometry, returns a list structure of points.

    Maybe use recurcion

    WKBGeometryTypes
    wkbPoint = 1,
    wkbLineString = 2,
    wkbPolygon = 3,
    wkbMultiPoint = 4,
    wkbMultiLineString = 5,
    wkbMultiPolygon = 6,
    wkbGeometryCollection = 7
    """
    ## Create root point list
    feature_point_stuct = []

    if geom.GetGeometryName() == "POINT":
        for point in geom.GetPoints():
            feature_point_stuct = point

    elif geom.GetGeometryName() == "LINESTRING":
        linePoints = geom.GetPoints()
        for point in linePoints:
            feature_point_stuct.append(point)

    elif geom.GetGeometryName() in ("POLYGON", "LINEARRING", "MULTIPOLYGON"):
        for indx in range(geom.GetGeometryCount()):
            subpoly_geom = geom.GetGeometryRef(indx)
            subpoly_struct = []

            if subpoly_geom.GetGeometryName() == "POLYGON":
                subpoly_geom = subpoly_geom.GetGeometryRef(0)

            for point in subpoly_geom.GetPoints():
                subpoly_struct.append(point)

            feature_point_stuct.append(subpoly_struct)

    else:
        print("There is an unexpected geometry type. WTF")
        print(geom.GetGeometryName())
        print()

    ## Return root point list
    return feature_point_stuct


def data_from_shapefile(shapefile_path):
    ## Setup driver for shapefile, open shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapefile = driver.Open(shapefile_path, 0)

    ## Test if file is readable
    if shapefile == None: print("Bad File."); exit()

    ## Get data layer
    layer = shapefile.GetLayer()

    ## Set int GetGeomType to string of geom type
    geometry_type = [None, 'point', 'line', 'polygon'][layer.GetGeomType()]

    ## Get layer field metadata
    attrib_data = layer.GetLayerDefn()

    ## Create list of attributes field names
    field_names = []
    field_count = attrib_data.GetFieldCount()
    for indx in range(field_count):
        field_data = attrib_data.GetFieldDefn(indx)
        field_names.append(field_data.GetName())

    ## Create lists to hold lists of attributes and geometrys
    attributes_list = []
    geometrys_list = []

    ## Loop through all features, loading attributes & geometry lists
    for feature in layer:
        feature_attributes = []
        for indx in range(field_count):
            feature_attributes.append(feature.GetField(indx))
        attributes_list.append(feature_attributes)
        geometrys_list.append(_get_geom_points(feature.GetGeometryRef()))

    ## Return New vector Layer
    return field_names, attributes_list, geometry_type, geometrys_list


def layer_from_shapefile(MapEngine_obj, shapefile_path):
    """
    """
    field_names, attributes_list, geometry_type, geometrys_list = data_from_shapefile(shapefile_path)
    return VectorLayer(MapEngine_obj, geometry_type, geometrys_list)



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
    """"""
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
