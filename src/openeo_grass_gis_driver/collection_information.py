# -*- coding: utf-8 -*-
from flask import make_response, jsonify, request
from openeo_grass_gis_driver.actinia_processing.actinia_interface import ActiniaInterface
from openeo_grass_gis_driver.collection_schemas import CollectionInformation, Extent, EoLinks
from openeo_grass_gis_driver.authentication import ResourceBase
from osgeo import osr, ogr

__license__ = "Apache License, Version 2.0"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2018, Sören Gebbert, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


strds_example = {
    "aggregation_type": "None",
    "bottom": "0.0",
    "creation_time": "2016-08-11 16:44:29.756411",
    "creator": "soeren",
    "east": "75.5",
    "end_time": "2013-07-01 00:00:00",
    "ewres_max": "0.25",
    "ewres_min": "0.25",
    "granularity": "1 month",
    "id": "precipitation_1950_2013_monthly_mm@PERMANENT",
    "map_time": "interval",
    "mapset": "PERMANENT",
    "max_max": "1076.9",
    "max_min": "168.9",
    "min_max": "3.2",
    "min_min": "0.0",
    "modification_time": "2016-08-11 16:45:14.032432",
    "name": "precipitation_1950_2013_monthly_mm",
    "north": "75.5",
    "nsres_max": "0.25",
    "nsres_min": "0.25",
    "number_of_maps": "762",
    "raster_register": "raster_map_register_934719ed2b4841818386a6f9c5f11b09",
    "semantic_type": "mean",
    "south": "25.25",
    "start_time": "1950-01-01 00:00:00",
    "temporal_type": "absolute",
    "top": "0.0",
    "west": "-40.5"
}


raster_example = {
    "cells": "2025000",
    "cols": "1500",
    "comments": "\"r.proj input=\"ned03arcsec\" location=\"northcarolina_latlong\" mapset=\"\\helena\" output=\"elev_ned10m\" method=\"cubic\" resolution=10\"",
    "creator": "\"helena\"",
    "database": "/tmp/gisdbase_75bc0828",
    "datatype": "FCELL",
    "date": "\"Tue Nov  7 01:09:51 2006\"",
    "description": "\"generated by r.proj\"",
    "east": "645000",
    "ewres": "10",
    "location": "nc_spm_08",
    "map": "elevation",
    "mapset": "PERMANENT",
    "max": "156.3299",
    "min": "55.57879",
    "ncats": "255",
    "north": "228500",
    "nsres": "10",
    "rows": "1350",
    "source1": "\"\"",
    "source2": "\"\"",
    "south": "215000",
    "timestamp": "\"none\"",
    "title": "\"South-West Wake county: Elevation NED 10m\"",
    "units": "\"none\"",
    "vdatum": "\"none\"",
    "west": "630000"
}


def coorindate_transform_extent_to_EPSG_4326(crs: str, extent: Extent):
    """Tranfor the extent coordinates to lat/lon

    :param crs:
    :param extent:
    :return:
    """

    source = osr.SpatialReference()
    source.ImportFromWkt(crs)

    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)

    transform = osr.CoordinateTransformation(source, target)

    lower_left = ogr.CreateGeometryFromWkt(f"POINT ({extent.spatial[0]} {extent.spatial[1]})")
    lower_left.Transform(transform)
    upper_right = ogr.CreateGeometryFromWkt(f"POINT ({extent.spatial[2]} {extent.spatial[3]})")
    upper_right.Transform(transform)

    a0 = lower_left.GetPoint()[0]
    a1 = lower_left.GetPoint()[1]
    a2 = upper_right.GetPoint()[0]
    a3 = upper_right.GetPoint()[1]

    extent.spatial = (a0, a1, a2, a3)
    return extent


class CollectionInformationResource(ResourceBase):

    def __init__(self):
        self.iface = ActiniaInterface()
        self.iface.set_auth(request.authorization.username, request.authorization.password)

    def get(self, name):

        # List strds maps from the GRASS location
        location, mapset, datatype, layer = self.iface.layer_def_to_components(name)

        status_code, layer_data = self.iface.layer_info(layer_name=name)
        if status_code != 200:
            return make_response(jsonify({"description": "An internal error occurred "
                                                         "while catching GRASS GIS layer information "
                                                         "for layer <%s>!\n Error: %s"
                                                         ""%(name, str(layer_data))}, 400))

        # Get the projection from the GRASS mapset
        status_code, mapset_info = self.iface.mapset_info(location=location, mapset=mapset)
        if status_code != 200:
            return make_response(jsonify({"description": "An internal error occurred "
                                                         "while catching mapset info "
                                                         "for mapset <%s>!"%mapset}, 400))

        extent = Extent(spatial=(float(layer_data["west"]), float(layer_data["south"]),
                                 float(layer_data["east"]), float(layer_data["north"])))

        title = "Raster dataset"
        if datatype.lower() == "strds":
            title = "Space time raster dataset"
            extent = Extent(spatial=(float(layer_data["west"]), float(layer_data["south"]),
                                     float(layer_data["east"]), float(layer_data["north"])),
                            temporal=(layer_data["start_time"], layer_data["end_time"]))
        if datatype.lower() == "vector":
            title = "Vector dataset"

        description = "GRASS GIS location/mapset path: /%s/%s" % (location, mapset)
        crs = mapset_info["projection"]

        coorindate_transform_extent_to_EPSG_4326(crs=crs, extent=extent)

        ci = CollectionInformation(name=name, title=title,
                                   description=description,
                                   extent=extent)

        return make_response(ci.to_json(), 200)
