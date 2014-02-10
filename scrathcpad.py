urlchars = ['$','-','_','.','+','!','*','\'','(',')',',','{','}','|','\'','^','~','[',']','`','<','>','#','%',';','/','?',':','@','&','=']

testcases = ["www.google.com","http://www.google.com","google.com"]
for longurl in testcases:
	longurl = longurl.lower()
	if(longurl[:11]=="http://www."):
		longurl= longurl[11:]
	if(longurl[:7]=="http://"):
		longurl= longurl[7:]
	if(longurl[:4]=="www."):
		longurl= longurl[4:]	
	print longurl