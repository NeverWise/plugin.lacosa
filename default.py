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
import os, re, xbmc, tools

# Entry point.
response = tools.getResponseUrl('http://www.beppegrillo.it/la_cosa')
phpPage = re.compile('Load JWPlayer.+?</script> --> <script src="(.+?)\.php"></script>').findall(response)[0]
response = tools.getResponseUrl(phpPage + '.php')
url = re.compile('{file: "(.+?)\.m3u8"}').findall(response)[0] + '.m3u8'

li = tools.createListItem('La Cosa', os.path.dirname(os.path.abspath(__file__)) + '/icon.png', '', 'video', { 'title' : 'La Cosa', 'Genre' : 'Intrattenimento, Notizie' })
xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).playStream(url, li)
