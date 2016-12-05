"""
A simple travian bot

"""
import re
from collections import namedtuple

import cookielib
import mechanize
from BeautifulSoup import BeautifulSoup

MAX_MAP_RESOURCES = 19

BASE_URL = 'http://ts1.travian.net/{}'
RESOURCES_URL = BASE_URL.format('build.php?id={}')
LOGIN_URL = BASE_URL.format('login.php')

Resource = namedtuple("Resource", "type_, level, link")


ResourceType = namedtuple("Resource", "lumberer, mine, barrier, farm")


class ResourcePriority(ResourceType):
    """
        Resources priority
    """
    def sorted(self):
        """
        Returns list of values, sorted

        """
        return list(dict(sorted(self._asdict().items(),
                                key=lambda x: x[1])).values())


class TravianBot:
    """
    Travian bot class

    """
    def __init__(self, user, password):
        self.can_build = False

        self.bro = mechanize.Browser()
        cookiejar = cookielib.LWPCookieJar()
        self.bro.set_cookiejar(cookiejar)

        self.login(user, password)
        self.resources = list(self.map_resources())

    def login(self, user, password):
        """ Login into travian """
        self.bro.open(LOGIN_URL)
        self.bro.select_form(name="login")
        self.bro["name"] = user
        self.bro["password"] = password
        self.bro.submit()

    def map_resources(self):
        """
        Resources generator

        """

        def filter_rendered(soup, attrs):
            """ Filter contents, and return the first rendered """
            return soup.findAll(attrs=attrs)[0].renderContents()

        for i in range(1, MAX_MAP_RESOURCES):
            resource_url = RESOURCES_URL.format(i)
            soup = self.get_soup(resource_url)
            tipe = filter_rendered(soup, {"class": "titleInHeader"})
            level = filter_rendered(BeautifulSoup(tipe), {"class": "level"})
            yield Resource(type_=tipe[0], level=level[-1], link=resource_url)

    def get_soup(self, url):
        """ Open a URL and returns its parsed BS content """
        self.bro.open(url)
        soup = BeautifulSoup(self.bro.response().read())
        return soup

    def build_resource(self, resource_id):
        """
        Build resource, accepts a resource id

        .. warning:: resource_id is incidentally auto_incremental.
                     and we're using that in our advantage here,
                     if that changes, self.resources should be
                     transformed to a dict and keep there resource_ids.

        """
        soup = self.get_soup(self.resources[resource_id].link)

        try:
            attrs = soup.findAll(attrs={"class": "green build"})[0].attrs
            link = re.match(".*'(.*)'.*", dict(attrs)['onclick']).group(1)
        except:
            raise ValueError("Already building or unable to build")

        return self.get_soup(BASE_URL.format(link))
