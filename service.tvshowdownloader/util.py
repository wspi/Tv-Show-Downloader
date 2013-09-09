import xbmc, xbmcgui, xbmcaddon, xbmcvfs, json, os, sys, urllib

try: import sqlite
except: pass
try: import sqlite3
except: pass

settings = xbmcaddon.Addon(id='service.tvshowdownloader')
downloadPath = settings.getSetting("downloadPath")
engines = []

if settings.getSetting("eztv") == "true":
   engines.append("resources.lib.engines.eztv.engine")

print engines
engines = map(lambda x: __import__(x, fromlist='.'),engines)

def syncShows():
    checkDB()
    shows = listShows()
    for engine in engines:
        print engine
        dir(engine)
	for show in shows:
            showInfo = lastEpisode(show['tvshowid'])
            name = show['title']
            season = showInfo[0]
            episode = showInfo[1]

            if name.startswith("The"):
                name = name[4:]
            id = engine.getID(name)
	    addShow(id, name, season, episode)

def searchEpisodes():
    for engine in engines:
        engine.searchEpisodes()

def connection():
    path = xbmc.translatePath('special://temp/')
    if not xbmcvfs.exists(path):
        print "Making path structure: " + path
        xbmcvfs.mkdir(path)
    path = os.path.join(path, 'showdownloader.db')
    try:
        if "sqlite3" in sys.modules:
            conn = sqlite3.connect(path, check_same_thread=False)
        elif "sqlite" in sys.modules:
            conn = sqlite.connect(path)
        else:
            print "ERROR! No Sql found"

        return conn
    except Exception, e:
        xbmcvfs.delete(path)

def checkDB():
    conn = connection()
    cursor = conn.cursor()
    try:
        cursor.execute("create table shows (name text unique, id integer, season integer, episode integer)")
        conn.commit()
    except:
	pass
    cursor.close()
    conn.close()
    print "Initialized DB"

	
def addShow(id, name, season, episode):
    conn = connection()
    cursor = conn.cursor()
    try:
        cursor.execute("insert into shows values (?, ?, ?, ?)", (str(name), int(id), int(season), int(episode)))
    except:
	cursor.execute("update shows set id=?, season=?, episode=? where name=?", (int(id), int(season), int(episode), str(name)))
    conn.commit()
    cursor.close()
    conn.close()


def lastEpisode(tvshowid):
    response = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "tvshowid":' + str(tvshowid) + ', "limits": { "start" : 0, "end": 1 }, "properties": ["season", "episode", "firstaired" ], "sort": { "order": "descending", "method": "label", "ignorearticle": true }}, "id": "libEpisodes"}'))
    episodes = response['result']['episodes']
    episode = [episodes[0]['season'], episodes[0]['episode']]
    return episode

def listShows():
    response = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "properties": ["title"] }, "id": "libTvShows"}'))
    shows = response['result']['tvshows']
    return shows
	
def extractAll(text, startText, endText):

    result = []
    start = 0
    pos = text.find(startText, start)
    while pos != -1:
        start = pos + startText.__len__()
        end = text.find(endText, start)
        result.append(text[start:end].replace('\n', '').replace('\t', '').lstrip())
        pos = text.find(startText, end)
    return result

def download(url):
    fileName = url.split('/')[-1]
    u = urllib.urlopen(url)
    destination = open(downloadPath + fileName, 'wb')
    meta = u.info()
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        destination.write(buffer)
    destination.close()


def getQuality():
    quality = settings.getSetting("quality")
    if quality == "0":
        quality = "720p"
    elif quality == "1":
        quality = "720p|hdtv"
    elif quality == "2":
        quality = "hdtv"
    elif quality == "3":
        quality = "hdtv|720p"
    elif quality == "4":
        quality = "first"
    return quality
