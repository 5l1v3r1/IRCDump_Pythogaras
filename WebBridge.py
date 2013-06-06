
from urllib import request
from IrcFuncs import privmsg
from re import compile
from os import environ

from DBFun import URLinDB, AddURL, URLRating, rmURL, GetURLID, PopURLs, SearchURLs, IsID, AddThumbUrl

import MakeThumb

shutup = 0
busy = False
current_url = "http://devel.graa.nl/"
m = ""
c = ""
helpdict = { "p" : "Get populair results. \"I want the top 3 populair\" = >p 3",
">" : "Add an url. \"I want to add an URL\" = >www.site.com description #tags, here",
"r" : "Remove an ID.",
"+" : "Increase rating of ID. \"I want to increase the rating of ID 1\" = >+ 1",
"-" : "Decrease rating of ID. \"I want to decrease the rating of ID 1\" = >- 1",
"s" : "Search trough URLs. \"I want to search for cats and display 3 results\" = >s 3 cats",
"su": "Make the bot shut up more." }

# try to GET url
def UrlGET(url):
	try:
		return request.urlopen(url).code
	except:
		return -1

# pm with possibility of shutting up
def ShutPM(chan, msg):
	global shutup
	if shutup == 0:	privmsg(chan, msg)
	
# check argument length
def ArgCheck(l):
	if len(m) < l:
		privmsg(c, "Missing argument")
		return False
	return True
	
# check if argument is integer
def isint(a):
	try:
		float(int(a))
		return True
	except:
		return False
		
# check if id exists with error message
def CheckID(id):
	if IsID(id):	return True
	else:
		privmsg(c, "No such ID") 
		return False
		
		
# show link-array in channel
def pmarr(sortedids, channel):
	for id,url,description,rating, date, tags in sortedids:
		rate = rating >= 0 and '+' or '-'
		rate = rate + str(rating)
		privmsg(channel, "-> " + current_url + str(id) + " | Description -> " + str(description) + " (" + rate + ")")
		#privmsg(channel, "Date -> " + str(date) + " | Tags -> " + str(tags))
	
# check command type
def EatCommand(onick, channel, message):
	global c, m
	m = message
	c = channel
	
	command = message[0].strip('>')
	if len(command) < 1:	return 0

	# is it an url?
	urlregex = compile("^(https?://)?(([\w!~*'().&=+$%-]+: )?[\w!~*'().&=+$%-]+@)?(([0-9]{1,3}\.){3}[0-9]{1,3}|([\w!~*'()-]+\.)*([\w^-][\w-]{0,61})?[\w]\.[a-z]{2,6})(:[0-9]{1,4})?((/*)|(/+[\w!~*'().;?:@&=+$,%#-]+)+/*)$")
	if urlregex.match(command):
		url = command
		
		if not ArgCheck(2):	return 0
		if not url.startswith("http://") and not url.startswith("https://"):	url = "http://" + url
		
		urlid = URLinDB(url)
		if urlid:
			ShutPM(channel, "URL already in DB, ID->" + str(urlid[0]))
			return 0
		if UrlGET(url) == 200:
			busy = True
			message[1] = message[1][0].upper() + message[1][1:]
			
			# split tags/description
			desc = ' '.join(message[1:])
			if "#" not in desc:
				ShutPM(channel, "Added: " + current_url + str(GetURLID(url)) + "/ | Description -> " + desc) if AddURL(url, onick, desc, "") else ShutPM(channel, "Error adding url")
			else:
				descarr = desc.split('#')
				if len(descarr) != 2:	ShutPM(channel, "Too much #'s")
				else: ShutPM(channel, "Added: " + current_url + str(GetURLID(url)) + "/ | Description -> " + descarr[0] + " | Tags -> " + descarr[1]) if AddURL(url, onick, descarr[0], descarr[1]) else ShutPM(channel, "Error adding url")
			# make thumbnail if possible
			thumbstatus = MakeThumb.MakeThumb(url, str(GetURLID(url)))
			if thumbstatus == 1 and AddThumbUrl(GetURLID(url)):	ShutPM(channel, "Made thumbnail")
			else:	ShutPM(channel, "Could not find fitting thumbnail image, code:" + str(thumbstatus))
		else:	ShutPM(channel, "Error validating URL, please provide a full and valid path")
			
	# change url rating
	elif command[0] == '+' or command[0] == '-' and len(message) == 2:
		if not ArgCheck(2):	return 0
		if not CheckID(message[1]):	return 0
		ShutPM(channel, "Changed rating") if URLRating(message[1], command[0]) else ShutPM(channel, "Error changing ratings")
			
	# remove url
	elif command == 'r':
		if not ArgCheck(2):	return 0
		if not CheckID(message[1]):	return 0
		ShutPM(channel, "Removed " + message[1]) if rmURL(message[1]) else ShutPM(channel, "Error removing")
		
	# get most populair urls
	elif command == 'p':
		if len(message) == 2:	sortedids = PopURLs(int(message[1]))
		if len(message) == 1:	sortedids = PopURLs(4)
		
		if not sortedids:
			privmsg(channel, "Error")
			return 0
		pmarr(sortedids, channel)
			
	# search urls		
	elif command == 's':
		if not ArgCheck(3):	return 0
		if not isint(message[1]):
			privmsg(channel, "Argument error")
			return 0
		try:
			sortedids = SearchURLs(' '.join(message[2:]), int(message[1]))
			if len(sortedids) == 0:
				privmsg(channel, "No results")
				return 0
		except:
			privmsg(channel, "Search error")
			return 0
			
		pmarr(sortedids, channel)

	# toggle reporting
	elif command == 'su':
		global shutup
		shutup = shutup == 0 and 1 or 0
		privmsg(channel, "Shutup flag is now " + str(shutup))
		
	# help
	elif command == 'help' or command == '?' or command == 'h':
		if len(message) == 2:
			try:
				privmsg(channel, helpdict[message[1]])
			except:
				privmsg(channel, "Command not found")
		elif len(message) == 1:
			privmsg(channel, "p <max?>, ><url> <description>, r <id>, +/- <id>, s <max> <string>, su, h(elp)|? <command>")
	
	else:	privmsg(channel, "Unknown command")
		
		