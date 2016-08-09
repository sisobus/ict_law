#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/ict_law_en/")
print sys.path

from ict_law.routes import app as application
