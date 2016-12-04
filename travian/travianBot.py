import mechanize
import Cookie
import cookielib
from BeautifulSoup import BeautifulSoup
import json

class Resource:
    def __init__(self, typ, level, link):
        self.typ = typ
        self.level = level
        self.link = link

class TravianBot:
   
        
    def getInfo(self):
        f = open("config.txt")
        data = json.load(f)
        self.user= str(data['login']['user'])
        self.password=str(data['login']['pass'])

    def login(self):
        self.br.open('http://ts1.travian.net/login.php')
        self.br.select_form(name="login")
        self.br["name"] = self.user
        self.br["password"] = self.password
        self.br.submit()

    def mapResources(self):
        for i in range(1,19):
            
            self.br.open('http://ts1.travian.net/build.php?id='+str(i))
            soup = BeautifulSoup(self.br.response().read())
            tipe = soup.findAll(attrs={"class" : "titleInHeader"})[0].renderContents()
            lev = BeautifulSoup(tipe).findAll(attrs={"class" : "level"})[0].renderContents()
            self.resources.append(Resource(tipe[0],lev[-1],('http://ts1.travian.net/build.php?id='+str(i))))

    def showMap(self):
        line=''
        for i in range(len(self.resources)):
            
            if(i%4==0):
                line = line + "("+self.resources[i].typ + "," + self.resources[i].level + ")"
                print line
                line = ''
            else:
                line = line + "("+self.resources[i].typ + "," + self.resources[i].level + ")"

        print line
            

    def __init__(self):
        self.br = mechanize.Browser()        
        cookiejar =cookielib.LWPCookieJar()
        self.br.set_cookiejar(cookiejar)
        self.resources=[]
        self.canBuild=False
        
        self.getInfo()
        self.login()
        self.mapResources()
