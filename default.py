#!/usr/bin/python
import neverwise as nw, re, sys, xbmcplugin#, datetime


class LaCosa(object):

  _handle = int(sys.argv[1])
  _params = nw.urlParametersToDict(sys.argv[2])

  def __init__(self):

    if len(self._params) == 0: # Visualizzazione del menu.

      # Shows.
      title = nw.getTranslation(30000)
      li = nw.createListItem(title, streamtype = 'video', infolabels = { 'title' : title })
      xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'id' : 'a', 'page' : self._getLaCosaUrl('archivio') }), li, True)

      shows = nw.getResponseBS(self._getLaCosaUrl('rubriche'))
      if shows.isSucceeded:
        shows = shows.body.findAll('div', 'icon_programmi')
        for show in shows:
          title = show.h3.a.text
          li = nw.createListItem(title, thumbnailImage = show.img['src'], streamtype = 'video', infolabels = { 'title' : title, 'plot' : show.p.text })
          xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'id' : 's', 'page' : show.a['href'] }), li, True)

      xbmcplugin.endOfDirectory(self._handle)

      if shows == None or not shows:
        nw.showNotification(nw.getTranslation(30001)) # Errore recupero shows.

    else:

      response = nw.getResponseBS(self._params['page'])
      if response.isSucceeded:

        # Archivio.
        if self._params['id'] == 'a':
          videos = response.body.find('div', id='video-recenti').findAll('div', 'video-block')
          for video in videos:
            title = re.search('<a title="(.+?)"', video.renderContents())
            if title != None:
              title = nw.htmlDecode(title.group(1))
              time = self._getTime(video)
              self._setEpItem(video, title, time)

          if len(videos) > 0:
            nextPage = response.body.find('span', 'current')
            nextPage = nextPage.findNext('a')
            if nextPage.get('class') and nextPage['class'] == 'page-numbers':
              nw.createNextPageItem(self._handle, nextPage.text, { 'id' : 'a', 'page' : nextPage['href'] })
            xbmcplugin.endOfDirectory(self._handle)
          else:
            nw.showNotification(nw.getTranslation(30002)) # Errore recupero dei videos shows.

        # Videos.
        if self._params['id'] == 's': # Visualizzazione dei videos di uno show.
          videos = response.body.find('div', id='recenti_canale').findAll('li')
          for video in videos:
            title = video.h4.text
            time = self._getTime(video)
            self._setEpItem(video, title, time)

          if len(videos) > 0:
            xbmcplugin.endOfDirectory(self._handle)
          else:
            nw.showNotification(nw.getTranslation(30002)) # Errore recupero dei videos shows.

        # Play video.
        elif self._params['id'] == 'v':
          title = response.body.find('meta', { 'property' : 'og:title' })['content']
          img = response.body.find('meta', { 'property' : 'og:image' })['content']
          descr = response.body.find('meta', { 'property' : 'og:description' })['content']
          streams = response.body.find('iframe')
          if streams != None:
            response = nw.getResponseForRegEx(streams['src'])
            found_stream = None

            if response.isSucceeded:
              streams = re.findall('mp4_[0-9]+":"(.*?)",', response.body)
              if not streams:
                streams = re.search('hd_src_no_ratelimit":"(.+?)"', response.body)
                found_stream = streams.group(1).replace('\/', '/')
              if streams == None:
                streams = re.search('sd_src_no_ratelimit":"(.+?)"', response.body)
                found_stream = streams.group(1).replace('\/', '/')
              if streams == None:
                streams = re.search('hd_src":"(.+?)"', response.body)
                found_stream = streams.group(1).replace('\/', '/')
              if streams == None:
                streams = re.search('sd_src":"(.+?)"', response.body)
                found_stream = streams.group(1).replace('\/', '/')

              if found_stream == None:
                for stream in reversed(streams):
                  if stream != '':
                    found_stream = stream
                    break

            if found_stream is not None:
              nw.playStream(self._handle, title, img, found_stream, 'video', { 'title' : title, 'plot' : descr })
            else:
              nw.showVideoNotAvailable() # Video non disponibile.
          else:
            nw.showVideoNotAvailable() # Video non disponibile.


  def _getLaCosaUrl(self, link):
    return 'http://www.la-cosa.it/{0}'.format(link)


  def _getTime(self, video):
    time = video.find('span', 'videoTime')
    if time != None:
      time = time.text.split(':')
      if len(time) == 1:
        time = time[0].split('.')
      if len(time) == 3:
        time = (int(time[0]) * 3600) + (int(time[1]) * 60) + int(time[2])
      else:
        time = (int(time[0]) * 60) + int(time[1])
    return time


  def _setEpItem(self, video, title, time):
    li = nw.createListItem(title, thumbnailImage = video.img['src'], streamtype = 'video', infolabels = { 'title' : title }, duration = time, isPlayable = True)
    xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'id' : 'v', 'page' : video.a['href'] }), li, False)


# Entry point.
#startTime = datetime.datetime.now()
lc = LaCosa()
del lc
#xbmc.log('{0} azione {1}'.format(nw.addonName, str(datetime.datetime.now() - startTime)))
