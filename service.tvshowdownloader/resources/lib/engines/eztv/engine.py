import util, urllib, re, sys

web = "http://eztv.it/"

def getID(name):
    url = urllib.urlopen(web)
    shows = url.read()
    url.close()

    shows = util.extractAll(shows, "<select name=\"SearchString\">", "</select>")
    shows = shows[0].strip()
    shows = util.extractAll(shows, "<option value=\"", "</option>")
    for show in shows:
        show = show.split("\">")
        if (re.search(name,show[1],re.IGNORECASE)):
            return (show[0])

def searchEpisodes():
    quality = util.getQuality()
    conn = util.connection()
    cursor = conn.cursor()
    cursor.execute('select * from shows')
    shows = cursor.fetchall()
    cursor.close()
    conn.close()
    for show in shows:
        name = show[0]
        currentEpisode = [int(show[2]), int(show[3])]
	newEpisodes = []
	processedEpisodes = []
        
        params = {"SearchString": show[1]}
        query = urllib.urlencode(params)
	url = str(web) + "/search/"

	tvShow = urllib.urlopen(url, query)
	episodes = tvShow.read()
	tvShow.close()

	episodes = util.extractAll(episodes, '<tr name="hover" class="forum_header_border">', '</tr>')
	for episode in episodes:
	    info = util.extractAll(episode, '<td class="forum_thread_post">', '</td>')
	    info = info[0].strip()
	    info = util.extractAll(info, 'class="epinfo">', '</a>')
            if (re.search('720p', info[0], re.I)):
	        info = re.findall(r'(\d{1,2})(?:e|x|episode)(\d{1,2})', info[0], re.I)
	        info = [int(info[0][0]), int(info[0][1]), "720p"]
	    else:
                info = re.findall(r'(\d{1,2})(?:e|x|episode)(\d{1,2})', info[0], re.I)
                info = [int(info[0][0]), int(info[0][1]), "hdtv"]
	
	    urls = util.extractAll(episode, '<td align="center" class="forum_thread_post">', '</td>')
	    linkNumber = re.findall('class="download_', urls[0], re.IGNORECASE)
	    linkNumber = len(linkNumber)
	    links = []
	    for link in (util.extractAll(urls[0], '</a><a href=\"', '"')):
	        links.append(link.strip())

	    if currentEpisode >= [info[0], info[1]]:
	        break
            else:
	        if quality.__contains__("|"):
                    prefer = quality.split("|")
                    if len(newEpisodes) > 0:
                        for newEpisode in newEpisodes:
                            if newEpisode.__contains__(info) or newEpisode.__contains__([info[0], info[1], prefer[0]]):
                                print "Episode already in download queue or preferred quality already found for " + str(name) + "!"
                                break
                            elif info == [info[0], info[1], prefer[0]] and newEpisode.__contains__([info[0], info[1], prefer[1]]):
                                print "Preferred Quality found, removing other qualities for " + str(name) + "!"
                                newEpisodes.append([info, links])
                                newEpisodes.remove(newEpisode)
                            else:
                                print "Newer Episode found for " + str(name) + "!"
                                newEpisodes.append([info, links])
                    else:
			print "Found new Episode for " + str(name) + "!"
                        newEpisodes.append([info, links]) 
                else:
                    if info[2] == quality or quality == "first":
                        newEpisodes.append([info, links])
                        break

	if len(newEpisodes) > 0:
	    for newEpisode in newEpisodes:
                try:
                    valid = False
    		    for link in newEpisode[1]:
		        url = urllib.urlopen(link)
		        if url.getcode() == 200:
		            util.download(link)
			    print "Downloading " + str(link)
			    valid = True
			    break
		    if valid == False:
		        print "No working link for " + str(name) + " Season: " + str(info[0]) + " Episode: " + str(info[1])
                except:
		    print "Unable to download: " + str(link)
	else:
	    print "No new episodes for " + str(name)
  
