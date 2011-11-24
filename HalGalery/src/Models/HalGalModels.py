from google.appengine.ext import db
from Models.BaseModels import Person
#{% block imports%}
#{%endblock%}
################
class Galery(db.Model):
    """TODO: Describe Galery"""
    Name= db.StringProperty(required=True, )
    Description= db.TextProperty()
    IsPublic= db.BooleanProperty()
    CreatedBy= db.ReferenceProperty(Person, collection_name='createdby_galeries', )
    PicasaUserId = db.StringProperty(required=True)
    
    @classmethod
    def CreateNew(cls ,name,description,ispublic,createdby,picasaUserId , _isAutoInsert=False):
        result = cls(
                     Name=name,
                     Description=description,
                     IsPublic=ispublic,                     
                     CreatedBy=createdby,
                     PicasaUserId=picasaUserId,)
        if _isAutoInsert: result.put()
        return result
    def __str__(self):
        return self.Name

## End Galery

class Album(db.Model):
    """TODO: Describe Album"""
    Name= db.StringProperty(required=True, )
    Galery= db.ReferenceProperty(Galery, collection_name='galery_albums', required=True, )
    DateCreated= db.DateProperty(auto_now_add=True, )
    CreatedBy= db.ReferenceProperty(Person, collection_name='createdby_albums', required=True, )
    ThumbUrl= db.LinkProperty()
    Description= db.TextProperty()
    
    @classmethod
    def CreateNew(cls ,name,galery,datecreated,createdby,thumburl,description , _isAutoInsert=False):
        result = cls(
                     Name=name,
                     Galery=galery,
                     DateCreated=datecreated,
                     CreatedBy=createdby,
                     ThumbUrl=thumburl,
                     Description=description,)
        if _isAutoInsert: result.put()
        return result
    def __str__(self):
        #TODO: Change the method to represent something meaningful
        return 'Change __str__ method' 
## End Album
