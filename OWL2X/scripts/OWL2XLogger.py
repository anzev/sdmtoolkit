# -*- coding: utf-8 -*-
"""
Logger setup for OWL2X.

@author: Anže Vavpetič, 2010 <anze.vavpetic@ijs.si>
"""
import logging

DEBUG = False

# Setup a logger
logger = logging.getLogger("OWL2X [Python]")
logger.setLevel(logging.DEBUG if DEBUG else logging.NOTSET)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(name)s %(levelname)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)