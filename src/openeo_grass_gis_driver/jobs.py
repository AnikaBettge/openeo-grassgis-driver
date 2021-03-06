# -*- coding: utf-8 -*-
from uuid import uuid4
from datetime import datetime
from flask import make_response, jsonify, request
from flask_restful import Resource
from openeo_grass_gis_driver.process_graph_db import GraphDB
from openeo_grass_gis_driver.job_db import JobDB
from openeo_grass_gis_driver.actinia_processing.actinia_interface import ActiniaInterface
from openeo_grass_gis_driver.job_schemas import JobInformation, JobList
from openeo_grass_gis_driver.error_schemas import ErrorSchema

__license__ = "Apache License, Version 2.0"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2018, Sören Gebbert, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


OUTPUT_FORMATS = {
    "default": "GTiff",
    "formats": {
        "GTiff": {
            "gis_data_types": ["raster"],
            "parameters": {
                "compress": {
                    "type": "string",
                    "description": "Set the compression to use.",
                    "default": "LZW",
                    "enum": ["LZW"]
                }
            }
        }
    }
}


class OutputFormats(Resource):

    def get(self, ):
        return make_response(jsonify(OUTPUT_FORMATS), 200)


class Jobs(Resource):
    """The /jobs endpoint implementation"""

    def __init__(self):
        self.iface = ActiniaInterface()
        self.graph_db = GraphDB()
        self.job_db = JobDB()

    def get(self):
        """Return all jobs in the job database"""
        # TODO: Implement user specific database access

        jobs = []

        for key in self.job_db:
            job = self.job_db[key]
            job.process_graph = None
            jobs.append(job)

        job_list = JobList(jobs=jobs)

        return make_response(job_list.to_json(), 200)

    def post(self):
        """Submit a new job to the job database"""
        # TODO: Implement user specific database access

        request_doc = request.get_json()

        if "process_graph" not in request_doc:
            error = ErrorSchema(id=uuid4(), message="A process graph is required in the request")
            return make_response(error.to_json(), 400)

        title = None
        if "title" in request_doc:
            title = request_doc["title"]

        description = None
        if "description" in request_doc:
            description = request_doc["description"]

        process_graph = request_doc["process_graph"]
        submitted = str(datetime.now())

        job_id = f"user-job::{str(uuid4())}"

        job_info = JobInformation(job_id=job_id, title=title,
                                  description=description,
                                  process_graph=process_graph,
                                  output=None, updated=None,
                                  submitted=submitted, status="submitted")
        self.job_db[job_id] = job_info

        return make_response(job_id, 201)

    def delete(self):
        """Clear the job database"""
        self.job_db.clear()
        return make_response("All jobs has been successfully deleted", 204)
