# -*- coding: utf-8 -*-
#{% block imports %}
import random
from lib.halicea.HalRequestHandler import HalRequestHandler as hrh
from lib.halicea.decorators import *
from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors
from lib import NewsFeed as nf
from lib.ascii2cyrillic import asciiToCyrillic as a2c
from lib.ascii2cyrillic import multiAsciiToCyrillic as ma2c 
import logging

#{% endblock}
#DICT_SIZE = 38932
DICT_SIZE = 200
from Models.DictModels import Word, WordForm , HtmlImport
import os
import sys
from google.appengine.api.datastore_errors import TransactionFailedError
class WordController(hrh):
    @Default('edit')
    def SetOperations(self):pass
    @View(templateName='Word_edit.html')
    def edit(self, *args):
        if self.params.key:
            item = Word.get(self.params.key)
            if item:
                result = {'op':'update', 'WordForm': WordForm(instance=item)}
                return result
            else:
                self.status = 'Word does not exists'
                self.redirect(WordController.get_url())
        else:
            return {'op':'insert' ,'WordForm':WordForm()}

    @AdminOnly()
    def delete(self, *args):
        if self.params.key:
            item = Word.get(self.params.key)
            if item:
                item.delete()
                self.status ='Word is deleted!'
            else:
                self.status='Word does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(WordController.get_url())
    @AdminOnly()
    @View(**{'templateName':'Word_index.html'})
    def index(self, *args):
        results =None
        index = 0; count=50
        try:
            index = int(self.params.index)
            count = int(self.params.count)
            if count<0:
                index += count
        except:
            pass
        r= Word.all().fetch(limit=abs(count), offset=index)
        index+=count
        return {'WordList':r, 'index':index, 'count':abs(count) }

    @AdminOnly()
    def save(self, *args):
        instance = None
        if self.params.key:
            instance = Word.get(self.params.key)
        form=WordForm(data=self.request.POST, instance=instance)
        if form.is_valid():
            result=form.save(commit=False)
            result.Value = result.Value.replace('<p>', '').replace('</p>', '')
#            result.Translation = result.Translation.strip('<p>') 
            result.put()
            self.status = 'Word is saved'
            self.redirect(WordController.get_url())
        else:
            self.SetTemplate(templateName = 'Word_edit.html')
            self.status = 'Form is not Valid'
            result = {'op':'update', 'WordForm': form}
            self.respond(result)

from Models.DictModels import Search, SearchForm
class SearchController(hrh):
    @ClearDefaults()
    @Default('search')
    @Handler('random', 'random')
    @Handler('atom', 'atom')
    def SetOperations(self): pass

    def replaceWithCyrillic(self, val):
        for k, v in ma2c.iteritems():
            val = val.replace(k, v)
        for k, v in a2c.iteritems():
            val = val.replace(k, v)
        return val
    def search(self, *args):
        if self.isAjax:
            return self.search_ajax()
        else:
            results = []
#            languages = Language.all().fetch(limit=100)
            transAvailable = []
            dictionaries = Dictionary.all().fetch(limit=1000)
            for dict in dictionaries:
                if not ([dict.Language1, dict.Language2] in transAvailable):  
                    transAvailable.append([dict.Language1, dict.Language2])
            searches = []
            for langPair in transAvailable:
                searches.append(
                                SearchForm(instance = Search.CreateNew('', langPair[0], langPair[1]))
                                )
            showMessage=False
            
            if self.params.text:
                showMessage=True
                val = self.replaceWithCyrillic(self.params.Text)
                results = Word.gql('WHERE Value= :v', v=val).fetch(limit=100)
            randomResults = self.randomSample(30, DICT_SIZE, 5)
            return {'SearchForms':searches,'results':results,
                          'showMessage':showMessage,
                          'randomResults':randomResults}
    def search_ajax(self, *args):
        self.SetTemplate(templateGroup='form', templateName='SearchForm_results.html')
        offset = self.params.offset and int(self.params.offset) or 0 
        results =[]
        showMessage=False
        sf = SearchForm(self.request.POST)
        if sf.is_valid():
            showMessage = True
            search = sf.save(commit=False)
            #search.Text = self.replaceWithCyrillic(search.Text)
            results = Word.gql('WHERE Value= :v', v=search.Text).fetch(limit=100, offset=offset)
            return {'results':results, 'showMessage':showMessage}
        else:
            return ''

    def random(self, *args):
        if self.isAjax:
            return self.random_ajax(*args)
        else: return self.search()
        
    def random_ajax(self, *args):
        self.SetTemplate('form', templateName='SearchForm_random.html')
        randomResults = self.randomSample(30, DICT_SIZE, 5)
        return {'randomResults':randomResults}
    def randomFeed(self):
#        self.respond(self.randomSample(30, DICT_SIZE, 5)[0])
        self.SetTemplate(templateGroup='form', 
                         templateName='AtomTemplate.txt')
        
        feed = nf.NewsFeed()
        randomResults = self.randomSample(30, DICT_SIZE, 5)
        for t in randomResults:
            entry = nf.FeedEntry(Title='')
            feed.Entries.append(object)
        return {}

    def randomSample(self, fr, to, cnt):
        offset = random.randint(fr, to)
        if offset+cnt>to:
            offset=to-cnt
        randomResults = Word.all().fetch(limit=cnt, offset=offset)
        result = randomResults
#        for t in range(0,cnt):
#            result.append(randomResults[random.randint(0,len(randomResults))])
        return result

from Models.DictModels import Importer, ImporterForm 
import pickle
import time
class ImporterController(hrh):
    def SetOperations(self):
        self.operations = { 'default':{'method':self.importHtml},
                            'import':{'method':self.importHtml},
                            'bulkDelete':{'method':self.bulkDelete}
                           }
    #@AdminOnly()
    def bulkDelete(self, *args):
        try:
            f=int(self.params.From)
            items = Word.all().fetch(limit=100, offset=0)
            if len(items)>0:
                db.delete(items)
                return str(f+100)
            else:
                return '-1'
            time.sleep(0.5)
        except TransactionFailedError, msg:
            logging.error(msg)
            return '-1'
        except Exception, msg:
            logging.error(msg)
            return '-1'
    def importHtml(self,*args):
        try:
            self.SetTemplate(templateName ='Importer_import.html')
            if self.method=='POST' and self.params.Html:
                imp = HtmlImport()
                imp.Html = self.params.Html
#                pdb.set_trace()
                WordList = imp.importHtml(self.params.Html)
                #d = {'Importer':imp, 'WordList':WordList, 'check':True}
                return len(WordList)
        except Exception, ex:
            logging.error(ex, ex.args)

from Models.DictModels import Language, LanguageForm 
class LanguageController(hrh):
    @AdminOnly()
    def SetOperations(self):pass
    @AdminOnly()
    def edit(self, *args):
        if self.params.key:
            item = Language.get(self.params.key)
            if item:
                result = {'op':'update', 'LanguageForm': LanguageForm(instance=item)}
                self.respond(result)
            else:
                self.status = 'Language does not exists'
                self.redirect(LanguageController.get_url())
        else:
            self.status = 'Key not provided'
            return {'op':'insert' ,'LanguageForm':LanguageForm()}

    @AdminOnly()
    def delete(self, *args):
        if self.params.key:
            item = Language.get(self.params.key)
            if item:
                item.delete()
                self.status ='Language is deleted!'
            else:
                self.status='Language does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(LanguageController.get_url())

    
    @View(templateName='Language.html')
    @Get()
    def index(self, *args):
        results =None
        index = 0; count=1000
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        result = {'LanguageList': Language.all().fetch(limit=count, offset=index)}
        result.update(locals())
        return result
    
    @AdminOnly()
    def save(self, *args):
        instance = None
        if self.params.key:
            instance = Language.get(self.params.key)
        form=LanguageForm(data=self.request.POST, instance=instance)
        if form.is_valid():
            result=form.save(commit=False)
            result.put()
            self.status = 'Language is saved'
            self.redirect(LanguageController.get_url())
        else:
            self.SetTemplate(templateName = 'Language_edit.html')
            self.status = 'Form is not Valid'
            result = {'op':'update', 'LanguageForm': form}
            return result

from Models.DictModels import Dictionary, DictionaryForm 
class DictionaryController(hrh):
    @AdminOnly()
    def SetOperations(self):pass
    def edit(self, *agrs):
        if self.params.key:
            item = Dictionary.get(self.params.key)
            if item:
                return  {'op':'update', 'DictionaryForm': DictionaryForm(instance=item)}
            else:
                self.status = 'Dictionary does not exists'
                self.redirect(DictionaryController.get_url())
        else:
            self.status = 'Key not provided'
            return {'op':'insert' ,'DictionaryForm':DictionaryForm()}

    def delete(self, *args):
        if self.params.key:
            item = Dictionary.get(self.params.key)
            if item:
                item.delete()
                self.status ='Dictionary is deleted!'
            else:
                self.status='Dictionary does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(DictionaryController.get_url())

    def index(self, *args):
        results =None
        index = 0; count=1000
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        result = {'DictionaryList': Dictionary.all().fetch(limit=count, offset=index)}
        result.update(locals())
        self.respond(result)

    def save(self, *args):
        instance = None
        form = None
        if self.params.key:
            instance = Dictionary.get(self.params.key)
            if instance:
                form=DictionaryForm(data=self.request.POST, instance=instance)
            else:
                form = DictionaryForm(self.request.POST)
        else:
            form = DictionaryForm(self.request.POST)
        if form.is_valid():
            result=form.save(commit=False)
            result.put()
            self.status = 'Dictionary is saved'
            self.redirect(DictionaryController.get_url())
        else:
            self.SetTemplate(templateName = 'Dictionary_edit.html')
            self.status = 'Form is not Valid'
            return {'op':'update', 'DictionaryForm': form}

from Models.DictModels import WordSugestion, WordSugestionForm 
class WordSugestionController(hrh):
    @Default('sugest')
    def SetOperations(self):pass

    @LogInRequired()
    def sugest(self, *args):
        if self.isAjax:
            return self.sugest_ajax()
        else:
            #TODO: Not Implemented yet
            pass
    @LogInRequired()
    def sugest_ajax(self, *args):
        if self.params.Wordkey and self.params.Sugestion:
            word = Word.get(self.params.Wordkey)
            sugestion = self.params.Sugestion
            sug = WordSugestion.CreateNew2(word, sugestion, self.User, _isAutoInsert=True)
            return "Suggestion is saved. Thanks for helping!"
        else:
            return "Cannot Add the Suggestion!"
    @AdminOnly()
    def show(self, *args):
        self.SetTemplate(templateName='WordSugestion_edit.html')
        if self.params.key:
            item = WordSugestion.get(self.params.key)
            if item:
                result = {'op':'update', 'WordSugestionForm': WordSugestionForm(instance=item)}
                self.respond(result)
            else:
                self.status = 'WordSugestion does not exists'
                self.redirect(WordSugestionController.get_url())
        else:
            self.status = 'Key not provided'
            return {'op':'insert' ,'WordSugestionForm':WordSugestionForm()}

    @AdminOnly()
    def delete(self, *args):
        if self.params.key:
            item = WordSugestion.get(self.params.key)
            if item:
                item.delete()
                self.status ='WordSugestion is deleted!'
            else:
                self.status='WordSugestion does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(WordSugestionController.get_url())


    def index(self, *args):
        results =None
        index = 0; count=1000
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        result = {'WordSugestionList': WordSugestion.all().fetch(limit=count, offset=index)}
        result.update(locals())
        return result


    def insert(self, *args):
        instance = None
        if self.params.key:
            instance = WordSugestion.get(self.params.key)
        form=WordSugestionForm(data=self.request.POST, instance=instance)
        if form.is_valid():
            result=form.save(commit=False)
            result.put()
            self.status = 'WordSugestion is saved'
            self.redirect(WordSugestionController.get_url())
        else:
            self.SetTemplate(templateName = 'WordSugestion_edit.html')
            self.status = 'Form is not Valid'
            return {'op':'update', 'WordSugestionForm': form}
