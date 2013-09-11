import util

util.sendNotification("Checking for new episodes manually", 3000)
print "Checking for new episodes manually"

util.syncShows()

util.searchEpisodes()
