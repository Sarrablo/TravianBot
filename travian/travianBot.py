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

class Priority:
    def __init__(self, l, m, b , g):
        self.l = l
        self.m = m
        self.b = b
        self.g = g
        
    def getMostPrior(self):
        foo = ["L","M","B","G"]
        bar =  [self.l,self.m,self.b,self.g]
        for i in range(4):
            for x in range(3):
                if(bar[x]<bar[x+1]):
                    a=bar[x]
                    bar[x]=bar[x+1]
                    bar[x+1] = a
                    z=foo[x]
                    foo[x]=foo[x+1]
                    foo[x+1]=z
        return foo
        
        
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
        self.resources=[]
        for i in range(1,19):
            
            self.br.open('http://ts1.travian.net/build.php?id='+str(i))
            soup = BeautifulSoup(self.br.response().read())
            tipe = soup.findAll(attrs={"class" : "titleInHeader"})[0].renderContents()
            lev = BeautifulSoup(tipe).findAll(attrs={"class" : "level"})[0].renderContents()
            self.resources.append(Resource(tipe[0],lev[-1],('http://ts1.travian.net/build.php?id='+str(i))))

    def buildResource(self, idResource):
        self.br.open(self.resources[idResource].link)
        soup = BeautifulSoup(self.br.response().read())
        link= None
        try:
            link = soup.findAll(attrs={"class" : "green build"})
        except:
            print "no se peude construir"
        if(len(link) > 0):
            foo= str(link).replace('&amp;','&')
            bar= foo[(foo.find('href'))+8:foo.find(';')-1]
            self.br.open('http://ts1.travian.net/'+bar)
        else:
            print "no se peude construir"
        
            

    def __init__(self):
        self.br = mechanize.Browser()        
        cookiejar =cookielib.LWPCookieJar()
        self.br.set_cookiejar(cookiejar)
        self.canBuild=False
        
        self.getInfo()
        self.login()
        self.mapResources()
