#-*- coding:utf-8 -*-
__author__ = 'sisobus'
import commands
import os
import json

ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','JPG','jpeg','JPEG','gif','GIF','zip'])

def allowedFile(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def createDirectory(directoryName):
    if not os.path.exists(directoryName):
        command = 'mkdir %s'%directoryName
        ret = commands.getoutput(command)
        command = 'chmod 777 %s'%directoryName
        ret = commands.getoutput(command)

