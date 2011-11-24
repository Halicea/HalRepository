from lib.djangoFormImports import widgets, fields, extras
from google.appengine.ext.db.djangoforms import ModelForm
from Models.HalGalModels import *
#{%block imports%}
#{%endblock%}
###############

class GaleryForm(ModelForm):
    class Meta():
        model=Galery
        exclude = ['CreatedBy',]
class AlbumForm(ModelForm):
    class Meta():
        model=Album
        #exclude
##End Album
class PicasaImage(object):
    def __init__(self, src, link, name, description, albumName, pos):
        self.src = src
        self.link = link
        self.name = name
        self.description = description
        self.albumName = albumName
        self.pos = pos
##End Galery


