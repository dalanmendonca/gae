from flask import Flask, render_template, request, redirect
import hashlib
import random
from google.appengine.ext import db

class ShortenedURLs(db.Model):
  hashedURL = db.StringProperty()
  originalURL = db.StringProperty()
  shortURL = db.StringProperty()

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




