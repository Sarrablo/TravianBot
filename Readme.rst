TravianBot
----------

Simple Travian bot.


Usage
-----

::

    >>> import travian
    >>> bot = travian.TravianBot("USER", "PASS")
    >>> bot.resources
    [<Resource type Lumberer level 1>,
     <Resource type Farm level 1>,
     <Resource type Lumberer level 0>,
     <Resource type Mine level 0>,
     <Resource type Barrier level 0>,
     <Resource type Barrier level 0>,
     <Resource type Mine level 0>,
     <Resource type Farm level 0>,
     <Resource type Farm level 0>,
     <Resource type Mine level 0>,
     <Resource type Mine level 0>,
     <Resource type Farm level 0>,
     <Resource type Farm level 0>,
     <Resource type Lumberer level 0>,
     <Resource type Farm level 0>,
     <Resource type Barrier level 0>,
     <Resource type Lumberer level 0>,
     <Resource type Barrier level 0>]

    >>> bot.build_resource(bot.resources[2])
    datetime.datetime(2016, 12, 5, 19, 39, 29, 171083)
