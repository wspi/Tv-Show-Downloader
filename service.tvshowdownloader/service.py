import sched, time, util, xbmcaddon

s = sched.scheduler(time.time, time.sleep)
global interval

def getInterval():
    settings = xbmcaddon.Addon(id='service.tvshowdownloader')
    return int(settings.getSetting("interval")) * 3600
   
def schedule(sc):
    interval = getInterval()
    util.sendNotification("Checking for new Episodes!", 3000)
    print "Checking interval: " + str(interval)
    util.syncShows()
    util.searchEpisodes()
    sc.enter(interval, 1, schedule, (sc,))

def run():
    schedule(s)
    s.run()
