from flask import Flask, render_template, request, redirect
import hashlib
import random
import json
from google.appengine.ext import db

class ShortenedURLs(db.Model):
  hashedURL = db.StringProperty()
  originalURL = db.StringProperty()
  shortURL = db.StringProperty()

class timelineData(db.Model):
  username = db.StringProperty()
  md5password = db.StringProperty()
  timelineConfig = db.TextProperty()  

app = Flask(__name__)
alphanumeric = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0']
specialchars = ['$','-','_','.','+','!','*','\'','(',')',',','{','}','|','\'','^','~','[',']','`','<','>','#','%',';','/','?',':','@','&','=']
legalchars  = alphanumeric + specialchars

@app.route('/')
def index():
    author = "dalan"
    name = "World"
    return render_template('index.html', author=author, name=name)

@app.route('/s')
def s():
    return render_template('s.htm')

@app.route('/outputpage', methods = ['POST'])
def outputpage():
	longurl = request.form["longurl"]
	longurl = longurl.lower()
	custom_request = request.form["customstring"]
	for x in longurl:
		if x not in legalchars: #The size of legal chars can be reduced because we're doing a conversion to lowercase
			return render_template('output.htm',errorcode=1)
	for x in custom_request:
		if x not in legalchars: #The size of legal chars can be reduced because we're doing a conversion to lowercase
			return render_template('output.htm',errorcode=1)					
	if(longurl[:11]=="http://www."):
		longurl= longurl[11:]
	if(longurl[:7]=="http://"):
		longurl= longurl[7:]
	if(longurl[:4]=="www."):
		longurl= longurl[4:]	
	

	hashObject = hashlib.md5(longurl)
	urlHash = hashObject.hexdigest()	
	q = ShortenedURLs.all()
	q.filter("hashedURL =",urlHash)
	results = q.fetch(1)
	q = ShortenedURLs.all()
	q.filter("shortURL =",custom_request)
	customCheck = q.fetch(1)
	if customCheck!=[]:
		custom_request=''
	#print len(results)
	if results==[]: 
		if custom_request=='':	
			shortURLExists  = True
			while (shortURLExists):
				newShortURL = ''.join(random.sample(alphanumeric,5))
			
				q.filter("shortURL =",newShortURL)
				results = q.fetch(1)
				if results==[]:
					shortURLExists = False


			new_record = ShortenedURLs(hashedURL=urlHash,originalURL=longurl,shortURL=newShortURL)
			new_record.put()
		else:
			print "Non empty custom request"
			newShortURL = custom_request
			new_record = ShortenedURLs(hashedURL=urlHash,originalURL=longurl,shortURL=newShortURL)
			new_record.put()

	else:
		print "URL already shortened"
		newShortURL = results[0].shortURL
	newShortURL = "app.dalanm.com/s/" + newShortURL	
	return render_template('output.htm',errorcode=0,finalurl=newShortURL)

@app.route('/s/<shortinput>')
def handle_short_input(shortinput):
    q = ShortenedURLs.all()
    q.filter("shortURL =",shortinput)
    results = q.fetch(1)
    if results==[]:
    	return render_template('error.htm')
    else:
    	destination=results[0].originalURL
    	startslab = destination[:4]
    	startslab = startslab.lower()
    	if startslab=='http':
    		pass
    	else:
    		destination = "http://" + destination
    	return redirect(destination)

@app.route('/t')
def t():
    return render_template('t.htm')

@app.route('/tnew', methods = ['POST'])
def tnew():
	uname = request.form["username"]
	pwd = request.form["password"]
	tdb = timelineData.all()
	tdb.filter("username =",uname)
	results = tdb.fetch(1)
	if results==[]:
		print "Username hasn't been used, awesome!"
		hashObject = hashlib.md5(pwd)
		urlHash = hashObject.hexdigest()	
		hashpwd = hashlib.md5(pwd).hexdigest()
		print uname
		print pwd
		print hashpwd

		new_timeline = timelineData(username=uname,md5password=hashpwd,timelineConfig="#UnconfiguredTimeline")
		new_timeline.put()
		return render_template('teditor.htm',new_user=True, uname=uname)
	else:
		print "Username is already taken"
		return render_template('terror.htm',errorcode=1)

@app.route('/treturning', methods = ['POST'])
def treturning():
	uname = request.form["username"]
	tdb = timelineData.all()
	tdb.filter("username =",uname)
	results = tdb.fetch(1)
	if results==[]:
		print "Username doesn't exist"
		return render_template('terror.htm',errorcode=2)
	else:
		x =  results[0]
		#print x.username
		#print x.md5password
		#print x.timelineConfig
		if x.timelineConfig=="#UnconfiguredTimeline":
			configured=False
			return render_template('teditor.htm',new_user=True)
		else:
			return render_template('teditor.htm',new_user=False, configdata=x.timelineConfig, uname=uname)

@app.route('/tconfigprocessor', methods = ['POST'])
def tconfigprocessor():		
	inputconfig = request.form["userconfig"]
	uname = request.form["username"]
	pwd = request.form["password"]
	hashpwd = hashlib.md5(pwd).hexdigest()
	tdb = timelineData.all()
	tdb.filter("username =",uname)
	results = tdb.fetch(1)
	x =  results[0]
	dbpwd = x.md5password
	if hashpwd==dbpwd:
		print "Passwords match!"
		#print type(x)
		x.timelineConfig = inputconfig
		x.put()
		destination = x.username
		destination = "/t/" + uname
		return redirect(destination)
	else:
		print "whoops your password was wrong :(, try again"
		return render_template('teditor.htm',new_user=False, configdata=inputconfig, uname=uname)
	#print inputconfig

@app.route('/t/<username>')
def handle_timeline(username):
	# The pattern below is used repeatedly, make a function out of it when efficiency matters
	tdb = timelineData.all()
	tdb.filter("username =",username)
	results = tdb.fetch(1)
	#results = tdb.fetch(1)
	if results==[]:
		print "Username doesn't exist"
		return render_template('terror.htm',errorcode=2)
	else:
		x =  results[0]
		configdata = x.timelineConfig
		print "Valid Username, attempting render"
		#configdata = configdata.replace('\n','***')
		configdata = json.dumps(configdata)
		return render_template('ttimeline.htm',configdata=configdata)






