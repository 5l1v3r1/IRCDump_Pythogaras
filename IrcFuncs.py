from socket import socket
from threading import Thread
from os import _exit, system, environ
from random import choice
from time import sleep

from DBFun import UserPass

# voor django functies
#from sys import path
#path.append("E:/WebIrcProject/Reddirc/")
#from Reddirc import settings
#from django.core.management  import setup_environ
#setup_environ(settings)
#from django.contrib.auth import authenticate

s = socket( )
NICK = ""
HOST = ""
startchan = "dumpbox"

def SChan():
	return '#'+startchan

# user input function
def userinput():
	chans = [startchan]
	currentchan = startchan

	while True:
		inp = input("")
		if inp == "":	continue
		# join channel
		elif inp[:4] == "join":
			sendor("JOIN :#" + inp[5:] + "\r\n")
			chans.append(inp[5:])
			currentchan = inp[5:]
		# part channel
		elif inp[:4] == "part":
			tmpchan = inp[5:]
			if tmpchan in chans:
				sendor("PART :#" + inp[5:] + "\r\n")
				chans.remove(inp[5:])
				if len(chans) == 0:
					print("Not on any channels anymore")
					currentchan = ""
				else:
					currentchan = choice(chans)
					print("Current channel: " + currentchan)
			else:	print("Not in channel")
		# switch channel
		elif inp[:6] == "swchan":
			tmpchan = inp[7:]
			if tmpchan in chans:
				currentchan = tmpchan
				print("Current channel: " + currentchan)
			else:	print("Not on channel")
		# private message
		elif inp[:2] == "pm":
			l = inp.split()
			privmsg(l[1], ' '.join(l[2:]))
		# list current channels (and crypt info)
		elif inp[:4] == "info":
			print("\tYour nick:\t\t\t" + NICK)
			print("\tServer:\t\t\t\t" + HOST)
			print("\tCurrent channels:\t\t" + ', '.join(["#" + chan for chan in chans]))
			print("\tActive channel:\t\t\t" + (currentchan == "" and "None" or "#" + currentchan))
		# commands
		elif inp[:4] == "help":	print("join, part, swchan, pm, info, code, r, cls, help, quit")
		# execute code from file 'code'
		elif inp == "code":
			print ("Executing external code from file code")
			fl = open('code','r')
			data = fl.read()
			fl.close()
			exec(data)
		elif inp == "cls":
			system("cls")
		# quit
		elif inp == "quit":
			print ("Shutting down, bleep")
			exitstring = "QUIT :Bot out\r\n"
			sendor(exitstring)
			print ("IRC Quit, bleep")
			sleep(1)
			_exit(1)
		# raw irc command
		elif inp[:2] == "r ":	sendor(inp[2:]+"\r\n")
		# normal chat
		else:
			if currentchan == "":
				print("Not on a channel")
				continue
			privmsg("#" + currentchan, inp)

# send binary
def sendor(str):
	s.send(str.encode('utf-8'))
	#print("\t\t(" + str.strip('\r\n') + ')')

# PM user/channel	
def privmsg(ent, st):
	sendor("PRIVMSG " + ent + " :" + st + "\r\n")
	
# read line, return tupple (nick, channel, message) of pm, if pm is directed to a channel
def GetMessage():
	line = ""
	while line[-4:] != '\\r\\n':
		inc = str(s.recv(1))
		if inc[2] == '\\':	line += inc[2:4]
		else:	line += inc[2:3]
	line = line[:-4]
	line=line.split()
	# respond to ping
	if (line[0]=="PING"):
		pong = "PONG " + line[1] + "\r\n"
		s.send(pong.encode('utf-8'))
	
	# if message to one of the channels, return (nick, channel, message)
	if len(line) > 3:
		onick =line[0].strip(':').split('!')[0]

		if line[1] == "PRIVMSG":
			pmchannel = line[2]
			pmmessage = line[3:]
			pmmessage[0] = pmmessage[0].strip(':')
			# direct messge
			if pmchannel == NICK:

				# auth user with django framework
				
				
				return False,0,0
			else:
				return onick, pmchannel, pmmessage
		else:	return False,0,0
	else:	return False,0,0

# connect to irc
def startirc(server, nicki):
	global NICK, HOST
	NICK = nicki
	HOST = server
	# connect
	PORT = 6667
	s.connect((server, PORT))
	
	# send ident info
	sendor("NICK " + NICK + "\r\n")
	sendor("USER Pybot " + server + " None :None\r\n")
	sleep(2)
	sendor("JOIN :#" + startchan + "\r\n")
	sendor("MODE #" + startchan + " +o Pythogaras\r\n")
	print("\t\tIRC to DB service running...")
	
	# user input thread
	t = Thread(target=userinput)
	t.start()

