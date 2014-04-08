#! /usr/bin/python
# coding: utf-8

import json
import urllib2
import re
import sys


XBMC_HOST = "192.168.178.50"
XBMC_PORT = 8080


def request(method, params = None, callback = None):
	data = {"jsonrpc": "2.0",
			"method": method,
			"id":1337,
			}

	if params is not None:
		data['params'] = params

	return send(data)

def send(data):
	xbmc_rpc_address = 'http://%s:%d/jsonrpc' % (XBMC_HOST, XBMC_PORT)

	print "==>\t%s" % json.dumps(data)

	req = urllib2.Request(xbmc_rpc_address, json.dumps(data), {'Content-Type': 'application/json'})

	response = urllib2.urlopen(req)
	res = json.loads(response.read())

	print "<==\t%s" % res
	return res


def open_url(url):
	request("Player.Open", { "item": {"file": url } })

def set_volume(volume):
	request("Application.SetVolume", { "volume": volume })

def play_pause():
	request("Player.PlayPause", { "playerid": get_current_player_id() })

def stop():
	request("Player.Stop", { "playerid": get_current_player_id() })

def get_current_player_id():
	'''
	Prüfen ob überhaupt ein Player läuft und erst dann Ergebnis zurück liefern!
	'''
	return request("Player.GetActivePlayers")['result'][0]['playerid']

def play_youtube(url):
	search = re.compile("v=([^&]+)")
	print search

	result = search.search(url)
	print result

	videoId = result.group(1)
	print videoId

	request("Player.Open", {"item": {"file": "plugin://plugin.video.youtube/?action=play_video&videoid=" + videoId } })

def play_url(url):
	# get site name
	site = None

	if url.startswith("magnet:"):
		site = "magnet"

	else:
		search = re.compile("(?:https|http)://(?:www\.)?([^\.]+)\.(?:[^/]+).+")
		result = search.search(url)

		if result:
			site = result.group(1)



	# regex from https://github.com/khloke/play-to-xbmc-chrome/blob/master/js/xbmc-helper.js
	sites = {
		"youtube" : 			{ "regex" : "v=([^&]+)",
									"handler" : "plugin://plugin.video.youtube/?action=play_video&videoid=<?>" },
		"mycloudplayersPlay" : 	{ "regex" : "play=([^&]+)",
									"handler" : "plugin://plugin.audio.soundcloud/?url=plugin://music/SoundCloud/tracks/<?>&permalink=<?>&oauth_token=&mode=15" },
		"vimeo" : 				{ "regex" : "^(?:https|http)://(?:www\.)?vimeo.com.*/(\\d+).*$",
									"handler" : "plugin://plugin.video.vimeo/?action=play_video&videoid=<?>" },
		"freeride" : 			{ "regex" : "^(?:https|http)://(?:www\.)?freeride.se.*/(\\d+).*$",
									"handler" : "http://v.freeride.se/encoded/mp4-hd/<?>.mp4" },
		"collegehumor" : 		{ "regex" : "(?:https|http)://(?:www\.)?collegehumor.com/[video|embed]+/([^_&/#\?]+)",
									"handler" : "plugin://plugin.video.collegehumor/watch/<?>/" },
		"dailymotion" : 		{ "regex" : "(?:https|http)://(?:www\.)?dailymotion.com/video/([^_&/#\?]+)",
									"handler" : "plugin://plugin.video.dailymotion_com/?url=<?>&mode=playVideo" },
		"ebaumsworld" : 		{ "regex" : "(?:https|http)://(?:www\.)?ebaumsworld.com/video/watch/([^_&/#\?]+)",
									"handler" : "plugin://plugin.video.ebaumsworld_com/?url=<?>&mode=playVideo" },
		"twitchtv" : 			{ "regex" : "^(?:https|http)://(?:www\.)?twitch.tv/([^_&/#\?]+).*$",
									"handler" : "plugin://plugin.video.twitch/playLive/<?>/" },
		"soundcloud" :			{ "regex" : "url=.+tracks%2F([^&]+)",
									"fetchSite" : "http://soundcloud.com/oembed?url=%s",
									"handler" : "plugin://plugin.audio.soundcloud/?url=plugin://music/SoundCloud/tracks/<?>&permalink=<?>&oauth_token=&mode=15" },
		"mixcloud" : 			{ "regex" : "(?:https|http)://(?:www\.)?mixcloud.com(/[^_&#\?]+/[^_&#\?]+)",
									"handler" : "plugin://plugin.audio.mixcloud/?mode=40&key=<?>" },
#    	"hulu" : 				{ "regex" : "(?:https|http)://(?:www\.)?hulu.com/watch/([^_&/#\?]+)",
#    								"handler" :  },
		"ardmediathek" : 	{ "regex" : "(?:https|http)://(?:www\.)?ardmediathek.de/.*?documentId=([^_&/#\?]+)",
									"handler" : "plugin://plugin.video.ardmediathek_de/?mode=playVideo&url=<?>" },
		"magnet" :				{ "regex" : "",
									"handler" : "plugin://plugin.video.xbmctorrent/play/<?>" },
	}


	if site in sites:
		if "fetchSite" in sites[site]:
			response = urllib2.urlopen(sites[site]["fetchSite"] % url)
			haystack = response.read()
		else:
			haystack = url

		if "regex" in sites[site] and sites[site]['regex'] is not None:
			needle = re.compile(sites[site]["regex"])
			matches = needle.search(haystack)

			if matches:
				videoId = matches.group(1)
				print "=!=\tFound video ID: %s" % videoId

		request("Player.Open", { "item": { "file": sites[site]["handler"].replace('<?>', videoId if videoId else url) } })
		return

	request("Player.Open", { "item": { "file": url } })

if __name__ == '__main__':
	if len(sys.argv) != 2:
		sys.exit("Usage: %s <url>" % sys.argv[0])
	else:
		#open_url(sys.argv[1])
		#play_youtube(sys.argv[1])
		#play_url(sys.argv[1])

		try: 
			{
				"play"	: play_pause,
				"pause"	: play_pause,
				"stop"	: stop,
			}[sys.argv[1]]()
		except KeyError:
			play_url(sys.argv[1])
