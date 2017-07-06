#-*- coding:utf-8 -*-
__author__ = 'sisobus'
import commands
import os
import json

ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','JPG','jpeg','JPEG','gif','GIF','zip'])

def allowedFile(filename):
    if filename.find('.') == -1:
        return filename in ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def createDirectory(directoryName):
    if not os.path.exists(directoryName):
        command = 'mkdir %s'%directoryName
        ret = commands.getoutput(command)
        command = 'chmod 777 %s'%directoryName
        ret = commands.getoutput(command)

def get_image_path(real_image_path):
    ret = ''
    for t in real_image_path.lstrip().rstrip().split('/')[6:]: ret=ret+t+'/'
    return ret[:-1]

def convert_email_to_directory_name(email):
    return email.replace('@','_at_')
