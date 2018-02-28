# -*- coding: utf-8 -*-
import os

class Config(object):
    HOST="http://localhost"
    PORT=8080
    LOCATION="ECAD"
    USER="user"
    PASSWORD="abcdefgh"
    # The database file that stores the graphs
    GRAPH_DB="%s/.graph_db_file.sqlite"%os.environ["HOME"]