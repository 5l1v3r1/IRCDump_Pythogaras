
import sqlite3
from string import ascii_uppercase, ascii_lowercase, digits
from random import choice
from datetime import datetime


con = 0
c = 0

################################################################# DB
# Load the database
def LoadDB(path):
	global con, c
	con = sqlite3.connect(path)		# , check_same_thread = False
	c = con.cursor()
	
# execute query
def ex(q, v):
	#try:
	c.execute(q, v)
	con.commit()
	return True
	#except:
	#	return False

################################################################# Users

# get user password hash
def UserPass(nick):
	ex("select password from auth_user where username = ?", (nick,))
	return c.fetchone()
		
		
################################################################# URLS
# check if URL is in DB
def URLinDB(url):
	ex("select id from IrcDump_link where url = ?", (url,))
	return c.fetchone()
	
# check if id exists
def IsID(id):
	ex("select url from IrcDump_link where id = ?", (id,))
	return c.fetchone()
	
# get the id from specific url
def GetURLID(url):
	ex('select id from IrcDump_link where url = ?', (url,))
	return c.fetchone()[0]
	
# insert new url entry
def AddURL(url, user, desc, tags):
	return ex('insert into IrcDump_link (url, user, description, rating, tags, thumburl, date) values (?,?,?,0.00,"",?,?)', (url, user, desc, tags, datetime.now()))

# increase or decrease url rating		
def URLRating(id, do):
	if do == '+' or do == '-':	return ex('UPDATE IrcDump_link SET rating = rating ' + do + ' 1 WHERE id = ?', (id,))
	
# add thumbnail url
def AddThumbUrl(id):
	turl = "IrcDump/img/thumbnails/thumb_" + str(id) + ".jpg"
	return ex('UPDATE IrcDump_link SET thumburl = ? where id = ?', (turl,id))
		
# remove id from database	
def rmURL(id):
	return ex('DELETE FROM IrcDump_link WHERE id = ?', (id,))
	
# get populair urls
def PopURLs(max):
	ex('SELECT id, url, description, rating, date, tags FROM IrcDump_link ORDER BY rating DESC LIMIT ?', (max,))
	return c.fetchall()
	
# search urls
def SearchURLs(s, max):
	ex('SELECT id, url, description, rating, date, tags FROM IrcDump_link WHERE description LIKE ? OR url LIKE ? ORDER BY rating DESC LIMIT ?', ('%'+s+'%', '%'+s+'%', max))
	return c.fetchall()
	