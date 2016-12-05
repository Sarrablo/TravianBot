"""
A simple travian bot

"""
import re
from collections import namedtuple
from datetime import datetime, timedelta

import cookielib
import mechanize
from BeautifulSoup import BeautifulSoup

BASE_URL = 'http://ts1.travian.net/{}'
RESOURCES_URL = BASE_URL.format('build.php?id={}')
LOGIN_URL = BASE_URL.format('login.php')

MAX_MAP_RESOURCES = 19
RES_TYPES = {'L': 'Lumberer', 'M': 'Mine', 'B': 'Barrier', 'G': 'Farm'}
INV_TYPES = {v: k for k, v in RES_TYPES.items()}

ResourceType = namedtuple("Resource", ",".join(RES_TYPES.values()))


class Resource(namedtuple("Resource", "id, type_, level, link")):
    """ Represents a resource """
    def __repr__(self):
        return "<Resource type {} level {}>".format(
            RES_TYPES[self.type_], self.level)


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


class ResourceList(list):
    """
    Represents a list of resources.

    """

    def get_lowest_by_type(self, type_):
        type_ = INV_TYPES[type_]
        results = [elem for elem in self if elem.type_ == type_]
        return sorted(results, key=lambda res: res.level)[0]

    def get_highest_by_type(self, type_):
        type_ = INV_TYPES[type_]
        results = [elem for elem in self if elem.type_ == type_]
        return sorted(results, key=lambda res: res.level, reverse=True)[0]


class TravianBot:
    """
    Travian bot class

    """
    def __init__(self, user, password):
        self.bro = mechanize.Browser()
        cookiejar = cookielib.LWPCookieJar()
        self.bro.set_cookiejar(cookiejar)

        self._can_build = True

        self.login(user, password)
        self.resources = ResourceList(self.map_resources())

    @property
    def can_build(self):
        """ Check if we can build something. """
        if not self._can_build:
            # We didn't got an exception, we check if the
            # last build has already finished...
            return self.last_build_known_ends < datetime.now()
        # Careful, if we build using another instance
        # of the bot, this might not be true
        return self._can_build


    def login(self, user, password):
        """ Login into travian """
        self.bro.open(LOGIN_URL)
        self.bro.select_form(name="login")
        self.bro["name"] = user
        self.bro["password"] = password
        self.bro.submit()

    def map_resources(self):
        """
        Generator yielding current resources available

        """

        def filter_rendered(soup, attrs):
            """ Filter contents, and return the first rendered """
            return soup.findAll(attrs=attrs)[0].renderContents()

        for i in range(1, MAX_MAP_RESOURCES):
            resource_url = RESOURCES_URL.format(i)
            soup = self.get_soup(resource_url)
            tipe = filter_rendered(soup, {"class": "titleInHeader"})
            level = filter_rendered(BeautifulSoup(tipe), {"class": "level"})
            yield Resource(id=i, type_=tipe[0], level=level[-1],
                           link=resource_url)

    def get_soup(self, url):
        """ Open a URL and returns its parsed BS content """
        self.bro.open(url)
        soup = BeautifulSoup(self.bro.response().read())
        return soup

    def build_resource(self, resource):
        """
        Build resource, accepts a resource id

        .. param:: resource: Resource object to build.

        """
        soup = self.get_soup(resource.link)

        try:
            attrs = soup.findAll(attrs={"class": "green build"})[0].attrs
            link = re.match(".*'(.*)'.*", dict(attrs)['onclick']).group(1)
            self._can_build = True
        except:
            self._can_build = False
            raise ValueError("Already building or unable to build")

        result = self.get_soup(BASE_URL.format(link))
        durationbox = result.findAll(attrs={"class": 'buildDuration'})[0]
        attrs = dict(durationbox.findAll(attrs={"class": "timer"})[0].attrs)
        return datetime.now() + timedelta(seconds=int(attrs['value']))
