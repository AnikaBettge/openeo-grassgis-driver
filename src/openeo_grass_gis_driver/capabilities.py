# -*- coding: utf-8 -*-
from flask import make_response, jsonify
from flask_restful import Resource

__license__ = "Apache License, Version 2.0"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2018, Sören Gebbert, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"

CAPABILITIES = {
    "version": "0.3.0",
    "endpoints": [
        {
            "path": "/capabilities",
            "methods": [
                "GET"
            ]
        }
    ]
}


class Capabilities(Resource):

    def get(self, ):
        return make_response(jsonify(CAPABILITIES), 200)


SERVICE_TYPES = {}


class ServiceTypes(Resource):

    def get(self, ):
        return make_response(jsonify(SERVICE_TYPES), 200)
