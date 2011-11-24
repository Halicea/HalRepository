from lib.halicea.HalRequestHandler import HalRequestHandler as hrh
from lib.halicea.decorators import *
from google.appengine.ext import db
import gdata.photos.service
import gdata.media
import gdata.geo

#{%block imports%}
from Models.HalGalModels import Galery
from Forms.HalGalForms import GaleryForm, PicasaImage

from Models.HalGalModels import Album
from Forms.HalGalForms import AlbumForm
#{%endblock%}
################################

class GaleryController(hrh):
    @Handler('view')
    @Handler('getpics')
    def SetOperations(self): pass
    
    def edit(self, *args):
        if self.params.key:
            item = Galery.get(self.params.key)
            if item:
                return {'op':'update', 'GaleryForm': GaleryForm(instance=item)}
            else:
                self.status = 'Galery does not exists'
                self.redirect(GaleryController.get_url())
        else:
            return {'op':'insert' ,'GaleryForm':GaleryForm()}

    def index(self, *args):
        self.SetTemplate(templateName="Galery_index.html")
        results =None
        index = 0; count=20
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        nextIndex = index+count;
        previousIndex = index<=0 and -1 or (index-count>0 and 0 or index-count) 
        result = {'GaleryList': Galery.all().fetch(limit=count, offset=index)}
        result.update(locals())
        return result
    def save(self, *args):
        instance = None
        if self.params.key:
            instance = Galery.get(self.params.key)
        form=GaleryForm(data=self.request.POST, instance=instance)
        if form.is_valid():
            result=form.save(commit=False)
            result.CreatedBy = self.User
            result.put()
            self.status = 'Galery is saved'
            self.redirect('/galery')
        else:
            self.SetTemplate(templateName = 'Galery_edit.html')
            self.status = 'Form is not Valid'
            return {'op':'update', 'GaleryForm': form}
    def details(self, *args):
        if self.params.key:
            item = Galery.get(self.params.key)
            if item:
                return {'Galery': Galery}
            else:
                self.status = 'Galery does not exists'
                self.redirect(GaleryController.get_url())
        else:
            self.status = 'Key not provided'
            return {'Galery':Galery}
    def delete(self,*args):
        if self.params.key:
            item = Galery.get(self.params.key)
            if item:
                item.delete()
                self.status ='Galery is deleted!'
            else:
                self.status='Galery does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(GaleryController.get_url())

    @View(templateName='Galery_index.html')
    def getpics(self, album):
        """Takes a feed from a Picasa album and shows all the pics.""" 
        #user = users.get_current_user() 
        #if user is None: 
        #    return http.HttpResponseForbidden('You must be signed in to add or  edit a route') 
#        gd_client = gdata.photos.service.PhotosService()
#        gd_client.email = 'costa@halicea.com'     # Set your Picasaweb e-mail address...
#        gd_client.password = 'arman1'  # ... and password
#        gd_client.source = 'api-sample-google-com'
#        gd_client.ProgrammaticLogin()
        
    
class AlbumController(hrh):
    def __init__(self, *args, **kwargs):
        super(AlbumController, self).__init__(*args, **kwargs)
    
    @Default('view')
    def SetOperations(self): pass
    
    @AdminOnly()
    def edit(self, *args):
        if self.params.key:
            item = Album.get(self.params.key)
            if item:
                return {'op':'update', 'AlbumForm': AlbumForm(instance=item)}
            else:
                self.status = 'Album does not exists'
                self.redirect(AlbumController.get_url())
        else:
            self.status = 'Key not provided'
            
            return {'op':'insert' ,'AlbumForm':AlbumForm()}
    @AdminOnly()
    def index(self, galery):
        results =None
        index = 0; count=20
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        nextIndex = index+count;
        previousIndex = index<=0 and -1 or (index-count>0 and 0 or index-count) 
        result = {'AlbumList': Album.all().fetch(limit=count, offset=index)}
        result.update(locals())
        return result
    
    @AdminOnly()
    def save(self, *args):
        instance = None
        if self.params.key:
            instance = Album.get(self.params.key)
        form=AlbumForm(data=self.request.POST, instance=instance)
        if form.is_valid():
            result=form.save(commit=False)
            result.put()
            self.status = 'Album is saved'
            self.redirect(AlbumController.get_url())
        else:
            self.SetTemplate(templateName = 'Album_edit.html')
            self.status = 'Form is not Valid'
            return {'op':'update', 'AlbumForm': form}
    
    @AdminOnly()
    def details(self, *args):
        if self.params.key:
            item = Album.get(self.params.key)
            if item:
                return {'Album': Album}
            else:
                self.status = 'Album does not exists'
                self.redirect(AlbumController.get_url())
        else:
            self.status = 'Key not provided'
            return {'Album':Album}
    
    @AdminOnly()
    def delete(self,*args):
        if self.params.key:
            item = Album.get(self.params.key)
            if item:
                item.delete()
                self.status ='Album is deleted!'
            else:
                self.status='Album does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(AlbumController.get_url())

    def view(self, album, *args):
        album = Album.get_by_key_name(album)
        gd_client = gdata.photos.service.PhotosService() 
        handle = album.Galery.PicasaUsername
        album_name=album 
        picset = [] 
        feed = gd_client.GetFeed('/data/feed/api/user/%s/album/%s? kind=photo' % (handle, album_name)) 
        for entry in feed.entry:
            if entry.geo.Point: 
                pos = entry.geo.Point.pos.text 
            else: 
                pos = '0 0'
            picsrc = entry.content.src 
            description = entry.summary.text 
            picLink = entry.link[1].href 
            logging.warn('-'.join([str(picsrc), str(description), str(picLink)]))
            picset.append( PicasaImage(picsrc, picLink, picsrc, description, album, pos) ) 
        return self.respond({'feed': picset})