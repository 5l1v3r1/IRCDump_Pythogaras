# https://github.com/reddit/reddit/blob/master/r2/r2/lib/scraper.py#L192

import re

from io import BytesIO
from PIL import Image
from gzip import GzipFile
from base64 import b64decode

from urllib.request import urlopen

webdir = "E:/WebIrcProject/IrcDump/Reddirc/"

# get site html
def GetHTML(url):
	try:
		response = urlopen(url)
		# some pages are gzipped, unzip em
		if response.info().get('Content-Encoding') == 'gzip':
			buf = BytesIO(response.read())
			f = GzipFile(fileobj=buf)
			data = f.read()
		else:	data = response.read()
	except:
		return -1

	return data

# filter image tags	
def FilterImageTags(data, url):
	# decode base64 scripts
	base64s = re.compile('[^\']<script.*?[^>]type="text/html64".*?>(.*?)</script>').findall(str(data))
	if len(base64s) != 0:
		for b in base64s:
			try:
				data += b64decode(b.replace('\\n', '').replace(' ','').encode('utf-8'))
			except:
				continue
	
	# get urls with image names in them
	imglinks = re.compile('[(\'"](http[^"\')]+(?:jpg|png|gif)[^)\'"]*)[)\'"]').findall(str(data))
	# get the urls from the image tags
	imgtaglinks = re.compile('[^\']<img.*?[^>]src=[\'|"](.*?)[\'"].*?>').findall(str(data))
	
	# all the links go full http link yeah
	for i,link in enumerate(imgtaglinks):
		if link.startswith('http'):	continue
		if url.endswith('/') and link.startswith('/'):
			imgtaglinks[i] = url + link[1:]
		else:
			imgtaglinks[i] = url + link
		if imgtaglinks[i] not in imglinks:
			imglinks.append(imgtaglinks[i])

	return imglinks
	
# download images
def GetBest(imagelinks):
	largest = 0
	best = -1
	done = []
	for imagelink in imagelinks:
		# alleen basic urls, net als reddit ^^
		if not imagelink.startswith(('http://', 'https://')):
			continue
		# download and verify images
		try:
			if imagelink in done:	continue
			tmpimage = urlopen(imagelink).read()
			done.append(imagelink)
			imio = Image.open(BytesIO(tmpimage))
			imio.verify()
			x,y = imio.size
			if x * y < 5000:	continue	# geen kleine images
			if x * y > largest:
				best = tmpimage
				largest = x * y
		except:
			continue
	return best

# make thumbnail
def MakeThumb(url, id):
	data = GetHTML(url)
	if data == -1:	return -1
	
	# check if url is image
	try:
		imio = Image.open(BytesIO(data))
		imio.verify()
		imio = Image.open(BytesIO(data))	# want verify is lame
		if imio.format == 'GIF':	imio = imio.convert('RGB')
		imio = imio.resize((38, 38), Image.ANTIALIAS)
		imio.save(webdir + "IrcDump/static/IrcDump/img/thumbnails/thumb_" + id + ".jpg", "JPEG")
		return 1
	except:
		pass
		
	imagelinks = FilterImageTags(data, url)
	if len(imagelinks) == 0:	return -2
	
	best = GetBest(imagelinks)
	if best == -1:	return -3

	try:
		f = Image.open(BytesIO(best))
		if f.format == 'GIF':	f = f.convert('RGB')
		f = f.resize((38, 38), Image.ANTIALIAS)
		f.save(webdir + "IrcDump/static/IrcDump/img/thumbnails/thumb_" + id + ".jpg", "JPEG")
	except:
		return -4
	
	return 1
	
	
	