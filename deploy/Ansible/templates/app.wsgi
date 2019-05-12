#! /usr/bin/python3

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp/FlaskApp/web")

from app import app as application
application.secret_key = "group68"
