# Graa 2013
# IRC to web bot (for Python 3.2 on Windows)
# 

# gejat log:
# http://daringfireball.net/2010/07/improved_regex_for_matching_urls
#

from sys import argv, path


from DBFun import LoadDB
LoadDB('E:/WebIrcProject/reddirc.sqlite')

from WebBridge import EatCommand
from IrcFuncs import GetMessage, startirc, SChan, privmsg
from threading import Thread



def main():
	busy = False
	startirc(argv[1], argv[2])

	# irc connection loop
	while 1:
		Onick, Channel, Message = GetMessage()
		if not Onick:	continue
		if len(Message[0]) == 0:	continue
		

		# Execute command
		try:
			if Message[0][0] == '>' and Channel == SChan():	EatCommand(Onick, Channel, Message)
			
		except:
			privmsg(Channel, "Lol I crashed")
			
		print(Onick + " -> " + Channel + " -> " + ' '.join(Message))

	
if __name__ == "__main__":
	if len(argv) < 3:
		print ("Lol read the code idiot")
		exit(0)
	main()