#!/usr/bin/env python
"""
File: dataloader.py
Author: Wen Li
Email: spacelis@gmail.com
Github: http://github.com/spacelis
Description:
    Loading bulk data into postgresql
"""

import sys
import imp
import click
import sqlalchemy as sa
from structing import CSVFile
from utils import aggregator
from utils import logging, LoggingThrottle, LOG_LVL_THROTTLED


logger = logging.getLogger(__name__)
logger.addFilter(LoggingThrottle(10))


def prepare_db(pg_url, meta):
    """ Prepare the database and create all tables

    :pg_url: TODO
    :meta: TODO
    :returns: TODO

    """
    engine = sa.create_engine(pg_url)
    meta.create_all(engine)
    return engine


def load_data(engine, all_tables, all_files, batch_size=10000, clear=False):
    """ Load data to the data base

    :arg1: TODO
    :returns: TODO

    """
    conn = engine.connect()
    for table, (file_name, headers) in zip(all_tables, all_files):
        if clear:
            conn.execute(table.delete())

        csvfile = CSVFile(file_name)
        csvfile.guess_structure()
        csvfile.headers = headers
        with csvfile:
            cnt = 0
            for batch_rows in aggregator(csvfile.row_set.dicts(), batch_size):
                conn.execute(table.insert(), batch_rows)
                cnt += len(batch_rows)
                logger.tinfo('%d rows loaded from %s', cnt, file_name)
            logger.info('FINISHED: %d rows loaded from %s', cnt, file_name)


@click.command()
@click.option('-b', '--buffer-size', default=10000, help='The size of batch for inserting operation.')
@click.option('-c', '--clear/--no-clear', default=False, help='Clear the table before loading')
@click.argument('spec_file', nargs=1)
@click.argument('pg_url', nargs=1)
def commandline(spec_file, pg_url, buffer_size, clear):
    """ Bulk Loading the data according to the spec

    :spec: The spec of the csv to load in the db
    :pg_url: The url for the database to load the data

    """
    spec = imp.load_source('', spec_file)
    engine = prepare_db(pg_url, spec.meta)
    load_data(engine, spec.all_tables, spec.all_files, buffer_size, clear)


if __name__ == "__main__":
    commandline()
