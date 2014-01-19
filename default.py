# Version 1.0.0 (16/09/2013)
# La Cosa
# Organo di comunicazione Movimento 5 Stelle.
# By NeverWise
# <mail>
# <url>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################
import sys, re, xbmcplugin, tools

# Entry point.
#startTime = datetime.datetime.now()

handle = int(sys.argv[1])
params = tools.urlParametersToDict(sys.argv[2])
idPlugin = 'plugin.lacosa'

if len(params) == 0: # Visualizzazione del menu.
  response = tools.getResponseUrl('http://www.beppegrillo.it/la_cosa')

  # Diretta.
  phpPage = re.compile('<div class="box_bottom">.+?<script src="(.+?)">').findall(response)[0]
  img = re.compile('<div class="logo">.+?<img.+?src="(.+?)".+?/>').findall(response)[0]
  live = tools.getResponseUrl(phpPage)
  url = re.compile('{file: "(.+?)\.m3u8"}').findall(live)[0] + '.m3u8'
  tools.addLink(handle, tools.getTranslation(idPlugin, 30001), img, '', 'video', { 'title' : 'La Cosa', 'plot' : '', 'duration' : -1, 'director' : '' }, url) # Diretta.

  # Show.
  show = re.compile('<div class="icon">(.+?)</div>').findall(response)[0]
  show = re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)"/></a>').findall(show)
  for link, img, title in show:
    title = tools.normalizeText(title)
    tools.addDir(handle, title, img, '', 'video', { 'title' : title, 'plot' : '', 'duration' : -1, 'director' : '' }, { 'id' : 's', 'page' : link })
  xbmcplugin.endOfDirectory(handle)
else:
  response = tools.getResponseUrl(params['page'])
  if params['id'] == 's': # Visualizzazione video di uno show.
    response = re.compile('<div.+?id="recenti_canale">(.+?)<div class="pagination">').findall(response)[0]
    response = re.compile('<a class="videoThumbnail" href="(.+?)"><img.+?src="(.+?)".+?/>.+?</a><h4><a.+?>(.+?)</a>').findall(response)
    for link, img, title in response:
      title = tools.normalizeText(title)
      tools.addDir(handle, title, img, '', 'video', { 'title' : title, 'plot' : '', 'duration' : -1, 'director' : '' }, { 'id' : 'v', 'page' : link, 'image' : img })
    xbmcplugin.endOfDirectory(handle)
  elif params['id'] == 'v': # Riproduzione del video.
    title = tools.normalizeText(re.compile('<h2 class="icon_article_left_title">(.+?)</h2>').findall(response)[0])
    descr = re.compile('<div class="icon_article_left_txt">(.+?)</div>').findall(response)[0]
    li = tools.createListItem(title, params['image'], '', 'video', { 'title' : title, 'plot' : tools.normalizeText(tools.stripTags(descr)), 'duration' : -1, 'director' : '' })
    streams = re.compile("file: '(.+?)'").findall(response)
    try:
      xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).playStream(streams[0], li)
    except:
      xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).playStream(streams[1], li)

#print 'La cosa azione ' + str(datetime.datetime.now() - startTime)
