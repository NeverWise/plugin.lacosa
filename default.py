#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, re, xbmcgui#, datetime
from neverwise import Util


class LaCosa(object):

  _handle = int(sys.argv[1])
  _params = Util.urlParametersToDict(sys.argv[2])

  def __init__(self):

    if len(self._params) == 0: # Visualizzazione del menu.

      items = []

      # Diretta.
      live = self._getLaCosaResponse('')
      if live != None:
        phpPage = re.compile('<div class="box_bottom">.+?<script src="(.+?)">').findall(live)[0]
        img = re.compile('<div class="logo.+?<img.+?src="(.+?)".+?/>').findall(live)[0]
        live = Util(phpPage).getHtml()
        if live != None:
          url = '{0}.m3u8'.format(re.compile('file: "(.+?)\.m3u8"').findall(live)[0])
          li = Util.createListItem(Util.getTranslation(30000), thumbnailImage = img, streamtype = 'video', infolabels = { 'title' : Util._addonName }) # Diretta.
          li.addStreamInfo('video', { 'aspect': 1.78, 'codec' : 'h264', 'width' : 640, 'height' : 360 })
          items.append([url, li, False, False])

      # Shows.
      shows = self._getLaCosaResponse('/rubriche')
      if shows != None:
        shows = re.compile('<div class="icon_programmi"> <a href="(.+?)"><img.+?src="(.+?)".+?/></a>.+?<a.+?>(.+?)</a>.+?<p>(.+?)</p>').findall(shows)
        for link, img, title, descr in shows:
          title = Util.normalizeText(title)
          li = Util.createListItem(title, thumbnailImage = img, streamtype = 'video', infolabels = { 'title' : title, 'plot' : Util.normalizeText(Util.trimTags(descr)) })
          items.append([{ 'id' : 's', 'page' : link }, li, True, True])

      if (live == None or not live) and (shows == None or not shows): # Se sono vuoti oppure liste vuote.
        Util.showConnectionErrorDialog() # Errore connessione internet!
      elif live == None or not live:
        xbmcgui.Dialog().ok(Util._addonName, Util.getTranslation(30001)) # Errore recupero stream diretta.
      elif shows == None or not shows:
        xbmcgui.Dialog().ok(Util._addonName, Util.getTranslation(30002)) # Errore recupero shows.

      # Show items.
      if len(items) > 0:
        Util.addItems(self._handle, items)

    else:

      response = Util(self._params['page']).getHtml(True)
      if response != None:

        # Videos.
        if self._params['id'] == 's': # Visualizzazione video di uno show.
          videos = re.compile('<div.+?id="recenti_canale">(.+?)<div class="pagination">').findall(response)[0]
          videos = re.compile('<a class="videoThumbnail.+?href="(.+?)">.+?<img.+?src="(.+?)".+?/>.+?(<span class="videoTime">.+?</span>)?</a>.+?<h4>(.+?)</h4>').findall(videos)
          items = []
          for link, img, time, title in videos:
            title = Util.normalizeText(title)
            if len(time) > 0:
              time = re.compile('<span class="videoTime">(.+?)</span>').findall(time)[0].split(':')
              if len(time) == 1:
                time = time[0].split('.')
              if len(time) == 3:
                time = (int(time[0]) * 3600) + (int(time[1]) * 60) + int(time[2])
              else:
                time = (int(time[0]) * 60) + int(time[1])
            li = Util.createListItem(title, thumbnailImage = img, streamtype = 'video', infolabels = { 'title' : title }, duration = time, isPlayable = True)
            items.append([{ 'id' : 'v', 'page' : link }, li, False, True])

          if len(items) > 0:
            Util.addItems(self._handle, items)
          else:
            xbmcgui.Dialog().ok(Util._addonName, Util.getTranslation(30003)) # Errore recupero video shows.

        # Play video.
        elif self._params['id'] == 'v':
          title = Util.normalizeText(re.compile('<meta property="og:title" content="(.+?)"/>').findall(response)[0])
          img = re.compile('<meta property="og:image" content="(.+?)"/>').findall(response)[0]
          descr = Util.normalizeText(Util.trimTags(re.compile('<meta property="og:description" content="(.+?)"/>').findall(response)[0]))
          streams = re.compile("file: '(.+?)'").findall(response)
          try:
            Util.playStream(self._handle, title, img, streams[0], 'video', { 'title' : title, 'plot' : descr })
          except:
            Util.playStream(self._handle, title, img, streams[1], 'video', { 'title' : title, 'plot' : descr })


  def _getLaCosaResponse(self, link):
    return Util('http://www.beppegrillo.it/la_cosa{0}'.format(link)).getHtml()


# Entry point.
#startTime = datetime.datetime.now()
lc = LaCosa()
del lc
#print '{0} azione {1}'.format(Util._addonName, str(datetime.datetime.now() - startTime))
