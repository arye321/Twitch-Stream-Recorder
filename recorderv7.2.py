import os.path
import time
import sys
import subprocess
import urllib2
__author__ = 'arye'

REFRESH = 60
CRASHREFRESH = 15

def main():

        streamer, quality = mainmenu()
        init_streamrecording(streamer, quality)
        firstloop = True
        while True:
            checkiflive(streamer.lower(), quality, firstloop)
            if firstloop:
                firstloop = False

def mainmenu():
    done = False

    while not done:
        streamer = getStreamerName()
        done = checkstreamername(streamer)

    done = False

    while not done:
        quality = raw_input('Enter quality 1.Low, 2.Medium, 3.High, 4.Best :')
        if quality == '1' or quality.lower() == 'low':
            quality = 'low'
            done = True
        elif quality == '2' or quality.lower() == 'medium':
            quality = 'medium'
            done = True
        elif quality == '3' or quality.lower() == 'high':
            quality = 'high'
            done = True

        elif quality == '4' or quality.lower() == "best":
            quality = 'best'
            done = True

        else:
            print 'wrong argument'
    return streamer, quality

#this method add streamers names into a text file and prints them when loading program
def getStreamerName():
    streamers = ""
    streamer = ""
    try:
        if os.path.isfile("StreamersList.txt"):
            streamersList = open("StreamersList.txt", "a+")
        else:
            streamersList = open("StreamersList.txt", "w+")

        streamers = streamersList.read()
        streamersList.close()
    except Exception:
        print
        print "Error: can't load SteamersList.txt"

    if len(streamers) > 0:
        streamers = streamers.split(',')
        print "Streamer list :"
        j = 1
        for streamerName in streamers:
            print str(j) + ") " + streamerName.capitalize()
            j += 1
    uinput = raw_input("Streamer Name:")
    streamer = uinput
    if uinput.isdigit() and int(uinput) >0 and int(uinput) < len(streamers)+1 and streamers>0:
        streamer = streamers[int(uinput)-1]
    else:
        try:
            streamersList= open("StreamersList.txt","a+")

            if not (uinput in streamers):

                if len(streamers)>0:
                    streamersList.write(",")
                streamersList.write(uinput)
            streamer = uinput

            streamersList.close()
        except Exception:
            print
            print "Error: can't load SteamersList.txt"



    return streamer


def checkstreamername(streamer):
    sys.stdout.write("Checking name...")
    url = 'https://api.twitch.tv/kraken/streams/' + streamer
    done = True
    try:
        urllib2.urlopen(url)

    except urllib2.HTTPError, e:
        print
        print('HTTPError = ' + str(e.code) + "(probably wrong stream name)")
        done = False
    except urllib2.URLError, e:
        print
        print('Error: cant connect to https://api.twitch.tv/kraken/streams/' + streamer)
        print 'Check your internet connection'
        done = False
    except Exception:
        print
        print ' error'
        done = False
    if done:
        print "OK"
    else:
        print "Stream name not working. Please try again."
    return done

def init_streamrecording(streamer, quality):
    print "Streamer: " + streamer
    print "Quality: " + quality
    print "Refresh time:" + str(REFRESH) + " secs)"
    print "Checking for stream... "

def checkiflive(streamer, quality, firstloop):
    url = 'https://api.twitch.tv/kraken/streams/' + streamer
    contents = '"stream":null'
    try:
        contents = urllib2.urlopen(url).read()


    except urllib2.URLError, e:
        print
        print('Error: cant connect to https://api.twitch.tv/kraken/streams/' + streamer )
        print 'Check your internet connection'
    except Exception:
        print
        print "Unknown error. Can't connect to twitch API for some reason."

    if '"stream":null' in contents:
        if firstloop:

            sys.stdout.write(time.strftime('%H:%M:%S : ') + streamer.title() + "'s stream is offline.")
        else:
            sys.stdout.write(".")
    else:
        golive(streamer, quality, firstloop)
        for i in range(10):
            if checkifstreamcrashed(streamer):
                print printtime() + ": Failed to reconnect, resuming normal refreshing (every " + str(
                    REFRESH) + " secs)"
                break
                # stream crashed and not resuming after 3min (18times*10sec)
            else:
                golive(streamer, quality, firstloop)

    time.sleep(REFRESH)


def golive(streamer, quality, firstloop):
    print
    print time.strftime('%H:%M:%S : ') + 'Stream is LIVE. running Livestreamer...'
    if firstloop:
        quality = checkquality(streamer, quality)

    try:
            os.system('livestreamer twitch.tv/' + streamer + ' ' + quality + ' -o ' + '"' + streamer + time.strftime(
            ' %d-%m-%Y %H-%M-%S.mp4"'))
    except Exception:
            print
            print "Could not run livestreamer..Program is ending"
            raw_input("Good bye")
            sys.exit()
def checkquality(streamer, quality):
        
    sys.stdout.write("Checking if " + quality + " quality avialable...")
    try:
            proc = subprocess.Popen(['livestreamer', 'twitch.tv/' + streamer],
                            stdout=subprocess.PIPE)
    

            while True:
                line = proc.stdout.readline()
                if line != '':

                    if quality in line.rstrip():
                        print 'OK'
                        return quality

                else:
                    print
                    print quality.title() + " quality is unavailable, switching to Best quality."
                    return 'best'
    except Exception:
        print
        print "Could not run livestreamer Program is ending"
        raw_input("Good bye")
        sys.exit()
def checkifstreamcrashed(streamer):
    print printtime() + ":Stream crashed. Trying to reconnect..."
    url = 'https://api.twitch.tv/kraken/streams/' + streamer
    contents= '"stream":null'
    for i in range(17):

        try:
            contents = urllib2.urlopen(url).read()

        except urllib2.URLError, e:

            if i == 0:
                sys.stdout.write("No internet connection.")
            else:
                sys.stdout.write(".")
        except Exception:
            if i == 0:
                sys.stdout.write("Unknown error..")
            else:
                sys.stdout.write(".")
        if '"stream":null' in contents:
            if i == 0:
                sys.stdout.write("Stream is offline.")
            else:
                sys.stdout.write(".")

        else:
            print
            return False
        time.sleep(CRASHREFRESH)
    print
    return True


def printtime():
    return time.strftime('%H:%M:%S')

main()
raw_input("Good Bye.")
