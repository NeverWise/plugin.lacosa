#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, re, xbmcplugin, xbmcgui#, datetime
from neverwise import Util


class LaCosa:

  __handle = int(sys.argv[1])
  __params = Util.urlParametersToDict(sys.argv[2])
  __idPlugin = 'plugin.lacosa'
  __namePlugin = 'La Cosa'
  __itemsNumber = 0

  def __init__(self):

    if len(self.__params) == 0: # Visualizzazione del menu.

      # Diretta.
      live = self.__getLaCosaResponse('')
      if live != None:
        phpPage = re.compile('<div class="box_bottom">.+?<script src="(.+?)">').findall(live)[0]
        img = re.compile('<div class="logo.+?<img.+?src="(.+?)".+?/>').findall(live)[0]
        live = Util(phpPage).getHtml()
        if live != None:
          url = '{0}.m3u8'.format(re.compile('file: "(.+?)\.m3u8"').findall(live)[0])
          Util.addItem(self.__handle, Util.getTranslation(self.__idPlugin, 30001), img, '', 'video', { 'title' : self.__namePlugin }, None, url, False) # Diretta.
          self.__itemsNumber += 1

      # Shows.
      shows = self.__getLaCosaResponse('/rubriche')
      if shows != None:
        shows = re.compile('<div class="icon_programmi"> <a href="(.+?)"><img.+?src="(.+?)".+?/></a>.+?<a.+?>(.+?)</a>.+?<p>(.+?)</p>').findall(shows)
        for link, img, title, descr in shows:
          title = Util.normalizeText(title)
          Util.addItem(self.__handle, title, img, '', 'video', { 'title' : title, 'plot' : Util.normalizeText(Util.trimTags(descr)) }, None, { 'id' : 's', 'page' : link }, True)
          self.__itemsNumber += 1

      if (live == None or not live) and (shows == None or not shows): # Se sono vuoti oppure liste vuote.
        Util.showConnectionErrorDialog(self.__namePlugin) # Errore connessione internet!
      elif live == None or not live:
        xbmcgui.Dialog().ok(self.__namePlugin, Util.getTranslation(self.__idPlugin, 30002)) # Errore recupero stream diretta.
      elif shows == None or not shows:
        xbmcgui.Dialog().ok(self.__namePlugin, Util.getTranslation(self.__idPlugin, 30003)) # Errore recupero streams shows.

    else:

      response = Util(self.__params['page']).getHtmlDialog(self.__namePlugin)
      if response != None:

        # Videos.
        if self.__params['id'] == 's': # Visualizzazione video di uno show.
          videos = re.compile('<div.+?id="recenti_canale">(.+?)<div class="pagination">').findall(response)[0]
          videos = re.compile('<a class="videoThumbnail.+?href="(.+?)">.+?<img.+?src="(.+?)".+?/>.+?(<span class="videoTime">.+?</span>)?</a>.+?<h4>(.+?)</h4>').findall(videos)
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
            Util.addItem(self.__handle, title, img, '', 'video', { 'title' : title }, time, { 'id' : 'v', 'page' : link }, True)
            self.__itemsNumber += 1

          if videos == None or not videos:
            xbmcgui.Dialog().ok(self.__namePlugin, Util.getTranslation(self.__idPlugin, 30003)) # Errore recupero video shows.

        # Play video.
        elif self.__params['id'] == 'v':
          title = Util.normalizeText(re.compile('<meta property="og:title" content="(.+?)"/>').findall(response)[0])
          img = re.compile('<meta property="og:image" content="(.+?)"/>').findall(response)[0]
          descr = Util.normalizeText(Util.trimTags(re.compile('<meta property="og:description" content="(.+?)"/>').findall(response)[0]))
          li = Util.createListItem(title, img, '', 'video', { 'title' : title, 'plot' : descr })
          streams = re.compile("file: '(.+?)'").findall(response)
          try:
            xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(streams[0], li)
          except:
            xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(streams[1], li)

    if self.__itemsNumber > 0:
      xbmcplugin.endOfDirectory(self.__handle)


  def __getLaCosaResponse(self, link):
    return Util('http://www.beppegrillo.it/la_cosa{0}'.format(link)).getHtml()


# Entry point.
#startTime = datetime.datetime.now()
lc = LaCosa()
del lc
#print '{0} azione {1}'.format(self.__namePlugin, str(datetime.datetime.now() - startTime))
