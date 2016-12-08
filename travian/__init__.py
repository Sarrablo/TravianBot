"""
A simple travian bot

Usage:
    travian --config config_file

Options:
    -h --help                   Show this screen
    -v --version                Show version
    --config <CONFIG_FILE>      Use given config file

Examples:
    travian --config ~/.travian_config.ini

"""

import re
import logging
from configparser import ConfigParser
from functools import lru_cache
from collections import namedtuple
from datetime import datetime, timedelta

from gettext import gettext as _
from docopt import docopt
from robobrowser import RoboBrowser
import io

logging.basicConfig()

DEFAULT_CONFIG = """
[urls]
base = http://ts1.travian.net/{}

[resources]
max = 19 """
RES_TYPES = {'L': _('Lumberer'), 'M': _('Mine'),
             'B': _('Barrier'), 'G': _('Farm')}
INV_TYPES = {v: k for k, v in RES_TYPES.items()}


ResourceType = namedtuple("Resource", ",".join(RES_TYPES.values()))


class Resource(namedtuple("Resource", "id, type_, level, link")):
    """ Represents a resource """
    def __repr__(self):
        return "<Resource type {} level {}>".format(self.type_, self.level)


class ResourcePriority(ResourceType):
    """
        Resources priority

        ResourcePriority(1, 2, 3, 4).sorted[0]
    """

    @property
    def sorted(self):
        """
        Returns list of values, sorted

        """
        return [a[0] for a in sorted(
            self._asdict().items(), key=lambda x: x[1], reverse=True)]


class ResourceList(list):
    """
    Represents a list of resources.

    """

    def get_lowest_by_type(self, type_):
        """ Get the lowest leveled resource of a specific type """
        type_ = INV_TYPES[type_]
        results = [elem for elem in self if elem.type_ == type_]
        return sorted(results, key=lambda res: res.level)[0]

    def get_highest_by_type(self, type_):
        """ Get the highest leveled resource of a specific type """
        type_ = INV_TYPES[type_]
        results = [elem for elem in self if elem.type_ == type_]
        return sorted(results, key=lambda res: res.level, reverse=True)[0]

    def _by_type(self):
        for name, type_ in INV_TYPES.items():
            yield name, [elem for elem in self if elem.type_ == type_]

    @property
    def by_type(self):
        """ Return resources ordered by type """
        return dict(self._by_type())

    def _level_by_type(self):
        for name, elems in self._by_type():
            yield name, sum([int(elem.level) for elem in elems])

    @property
    def level_by_type(self):
        """ Return levels ordered by type """
        return dict(self._level_by_type())


class Travian:
    """
    Travian Interface

    """
    def __init__(self, config):
        self.config = config
        self.busy_until = None
        self.bro = RoboBrowser(history=True)
        self._can_build = True
        self.urls = dict(config.items("urls"))
        self.login(config.get('login', 'user'), config.get('login', 'pass'))

    @property
    def can_build(self):
        """ Check if we can build something. """
        if not self._can_build:
            # We didn't got an exception, we check if the
            # last build has already finished...
            return self.busy_until < datetime.now()
        # Careful, if we build using another instance
        # of the bot, this might not be true
        return self._can_build

    def login(self, user, password):
        """ Login into travian """
        self.bro.open(self.urls['base'].format('login.php'))
        form = self.bro.get_form()
        form["name"].value = user
        form["password"].value = password
        self.bro.submit_form(form)

    def _get_resource(self, res):
        """
        Return a resource level / type given its id.

        """
        resource_url = self.urls['base'].format('build.php?id={}'.format(res))
        self.bro.open(resource_url)
        tipe = self.bro.select('.titleInHeader')[0]
        type_, level = re.match("(.*) .* (.*)", tipe.text).groups()
        return Resource(id=res, type_=type_, level=level, link=resource_url)

    def _get_resources(self):
        """
        Generator yielding current resources available

        """

        for res in range(1, int(self.config.get("resources", "max"))):
            yield self._get_resource(res)

    @property
    @lru_cache(10)
    def resources(self):
        """
        Generator yielding current resources available

        """
        return ResourceList(self._get_resources())

    def build_resource(self, resource):
        """
        Build resource, accepts a resource id

        .. param:: resource: Resource object to build.

        """
        self.bro.open(resource.link)

        try:
            onclick = self.bro.select('.green.build')[0].attrs['onclick']
            link = re.match(".*'(.*)'.*", onclick).group(1)
            self._can_build = True
        except:
            self._can_build = False
            raise ValueError("Already building or unable to build")

        self.bro.open(self.urls['base'].format(link))
        duration = self.bro.select('.buildDuration')[0].find().attrs['value']
        self.busy_until = datetime.now() + timedelta(seconds=int(duration))
        return self.busy_until


class TravianBot:
    """
    Travian bot
    """
    def __init__(self, config):
        self.config = config
        self.travian = Travian(config)

    def assess_resources(self):
        """
        Assess resources

        """
        groups = self.travian.resources.by_type
        logging.debug(groups)

    def run(self):
        """
        run

        """
        raise NotImplementedError()


def get_config(where):
    """
    Generate a config parser filled with default travian values

    """
    config = ConfigParser()
    config.read_file(io.StringIO(DEFAULT_CONFIG))
    if where:
        config.read(where)
    return config


def simple_login(user, pass_):
    """
    Return a simple conffile with login

    """
    config = get_config(False)
    config.add_section("login")
    config.set('login', 'user', user)
    config.set('login', 'pass', pass_)
    return config


def main():
    """
    Entry point

    """
    args = docopt(__doc__)
    TravianBot(get_config(args.config)).run()


if __name__ == "__main__":
    main()
