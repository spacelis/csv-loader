#!/usr/bin/env python
"""
File: utils.py
Author: Wen Li
Email: spacelis@gmail.com
Github: http://github.com/spacelis
Description:
    Some utility functions for running the data loader.
"""

import itertools as it
import logging
from time import time

LOG_LVL_THROTTLED=15
logging.addLevelName(LOG_LVL_THROTTLED, 'TINFO')
def tinfo(self, message, *args, **kws):
    if self.isEnabledFor(LOG_LVL_THROTTLED):
        self._log(LOG_LVL_THROTTLED, message, args, **kws)
logging.Logger.tinfo = tinfo

logging.basicConfig(level=LOG_LVL_THROTTLED,
                    format='%(asctime)-15s [%(levelname)s] [%(module)s] %(message)s')


class LoggingThrottle(logging.Filter):

    """ Throttling logging messages """

    def __init__(self, min_interval=1):
        """TODO: to be defined1. """
        logging.Filter.__init__(self)
        self._min_interval = min_interval
        self._last_event = time()

    def filter(self, record):
        """TODO: Docstring for filter.

        :record: TODO
        :returns: TODO

        """
        ts = time()
        if record.levelno == LOG_LVL_THROTTLED:
            toshow = (ts > self._last_event + self._min_interval)
            if toshow:
                self._last_event = ts
                return True
        else:
            return True
        return False


def get_connection(url):
    """ Return an connection. """
    passwd = urllib.quote(getpass.getpass())
    if '@' in url:
        url_pw = url.replace('@', passwd + '@')
    else:
        url_pw = url.replace('://', '://{0}:{1}@'.format(getpass.getuser(), passwd))
    return create_engine(url_pw)


def alternating(iterable, n=1000):
    while True:
        for c in it.cycle(iterable):
            for i in it.repeat(c, n):
                yield i

def aggregator(iterable, n=1000):
    for _, g in it.groupby(it.izip(alternating('ab', n), iterable), key=lambda x: x[0]):
        yield [x[1] for x in g]
