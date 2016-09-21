import os.path
import time
import sys
import subprocess
import urllib2
import webbrowser
__author__ = 'arye'

REFRESH = 60
CRASHREFRESH = 15
oauth= ''
def main():
    
    global oauth
    print 'Twitch Recorder'
    try:
        if os.path.isfile("oauth.txt"):
            txtfile = open("oauth.txt", "a+")
        else:
            txtfile = open("oauth.txt", "w+")

        oauth = txtfile.read()
        txtfile.close()
   
        
    except Exception:
        print
        print "Error: can't load oauth.txt"
        
    if oauth == '':
        print "Error - Did not find oauth"
        print "Please enter oauth in oauth.txt"
        print "Do you want to open https://blog.twitch.tv/client-id-required-for-kraken-api-calls-afbb8e95f843 to get oauth now? y/n"
        if raw_input().lower() == 'y':
            openOauthSite()

        if (raw_input("Do you want to enter Oauth now? y/n :")).lower() == 'y' :
            oauth = raw_input("Enter oauth :")
            try:
                oauthTxt= open("oauth.txt","a+")
                print "Saving oauth to oauth.txt..."
                
                if 'oauth:' in oauth:
                    oauth = oauth [6:]
                    print 'oauth = ' + oauth
                oauthTxt.write(oauth)
                print "Done."
            
                oauthTxt.close()
                  
            except Exception,e:
                    print e
                    print "Error: can't load oauth.txt"
        else:
            #no oauth  - quiting app
            return


    streamer, quality = mainmenu()
    init_streamrecording(streamer, quality)
    firstloop = True
    while True:
            checkiflive(streamer.lower(), quality, firstloop)
            if firstloop:
                firstloop = False

def mainmenu():


    streamer = getStreamerName()
        

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
    done = False
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
    while not done:
            uinput = raw_input("Streamer Name:")
            streamer = uinput
            if uinput.isdigit() and int(uinput) >0 and int(uinput) < len(streamers)+1 and streamers>0:
                streamer = streamers[int(uinput)-1]
                done = True
            else:
                try:
                    streamersList= open("StreamersList.txt","a+")

                    if not (uinput in streamers):
                        if checkstreamername(streamer):
                            done = True
                            if len(streamers)>0:
                                streamersList.write(",")
                            streamersList.write(uinput)
                    else :
                        done = True

                    streamer = uinput

                    streamersList.close()
                  
                except Exception,e:
                    print e
                    print "Error: can't load SteamersList.txt"



    return streamer

def checkstreamername(streamer):
    sys.stdout.write("Checking name...")
    url = 'https://api.twitch.tv/kraken/streams/' + streamer + '?client_id='+ oauth
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
        print 'Check your internet connection OR problem with OAUTH '
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
    url = 'https://api.twitch.tv/kraken/streams/' + streamer+ '?client_id=' + oauth
    contents = '"stream":null'
    try:
        contents = urllib2.urlopen(url).read()


    except urllib2.URLError, e:
        print
        print('Error: cant connect to https://api.twitch.tv/kraken/streams/' + streamer )
        print 'Check your internet connection OR problem with OAUTH '
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
    
            
            os.system('livestreamer' + '  --http-header Client-ID='+oauth +' twitch.tv/' + streamer +' ' + quality + ' -o ' + '"' + streamer + time.strftime(
            ' %d-%m-%Y %H-%M-%S.mp4"'))
    except Exception:
            print
            print "Could not run livestreamer..Program is ending"
            raw_input("Good bye")
            sys.exit()
def checkquality(streamer, quality):
        
    sys.stdout.write("Checking if " + quality + " quality avialable...")
    try:
            proc = subprocess.Popen(['livestreamer', 'twitch.tv/' + streamer,'--http-header','Client-ID='+oauth],
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
    url = 'https://api.twitch.tv/kraken/streams/' + streamer + '?client_id='+ oauth
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
def openOauthSite():
    print "Opening https://blog.twitch.tv/client-id-required-for-kraken-api-calls-afbb8e95f843"
    print "..."
    webbrowser.open('https://blog.twitch.tv/client-id-required-for-kraken-api-calls-afbb8e95f843') 

main()
raw_input("Good Bye.")
