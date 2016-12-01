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
from time import time
import click
import sqlalchemy as sa
from structing import CSVFile
from utils import aggregator, get_connection
from utils import logging, LoggingThrottle


logger = logging.getLogger(__name__)
logger.addFilter(LoggingThrottle(10))


def prepare_db(pg_url, meta, force_recreate=False):
    """ Prepare the database and create all tables

    :pg_url: TODO
    :meta: TODO
    :returns: TODO

    """
    engine = sa.create_engine(get_connection(pg_url))
    if force_recreate:
        meta.drop_all(engine)
    meta.create_all(engine)
    return engine


def load_data(engine, all_tables, all_files, batch_size=10000):
    """ Load data to the data base

    :arg1: TODO
    :returns: TODO

    """
    total_start = time()
    conn = engine.connect()
    for table, csvfile in zip(all_tables, all_files):
        with csvfile:
            cnt = 0
            file_start = time()
            for batch_rows in aggregator(csvfile.row_set.dicts(), batch_size):
                conn.execute(table.insert(), batch_rows)
                cnt += len(batch_rows)
                logger.tinfo('%d rows loaded from %s', cnt, csvfile.file_name)
            logger.info('FINISHED: %d rows loaded in %.2fs from %s',
                        cnt, time() - file_start, csvfile.file_name)
    logger.info('Suceeded: %d tables loaded in %.2fs', len(all_tables), time() - total_start)


@click.command()
@click.option('-b', '--buffer-size', default=10000,
              help='The size of batch for inserting operation.')
@click.option('-f', '--force-recreate/--no-force-recreate', default=False,
              help='Force recreate the table before loading')
@click.argument('spec_file', nargs=1)
@click.argument('pg_url', nargs=1)
def console(spec_file, pg_url, buffer_size, force_recreate):
    """ Bulk Loading the data according to the spec

    :spec: The spec of the csv to load in the db
    :pg_url: The url for the database to load the data

    """
    spec = imp.load_source('', spec_file)
    engine = prepare_db(pg_url, spec.meta, force_recreate)
    load_data(engine, spec.all_tables, spec.all_files, buffer_size)


if __name__ == "__main__":
    console()
