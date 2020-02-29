#!/usr/bin/python3

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp/web")
sys.path.append('/home/ubuntu/.local/lib/python3.6/site-packages')
sys.path.append('/var/www/FlaskApp/web/resources')
sys.path.append('/var/www/FlaskApp/web/static')
sys.path.append('/var/www/FlaskApp/web/templates')
sys.path.append('/var/www/FlaskApp/web/utils')

print(sys.path)

from app import app as application
application.secret_key = "group68"