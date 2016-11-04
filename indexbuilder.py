import urllib
import getpass
import click
from sqlalchemy import create_engine, Table, MetaData, Index
from sqlalchemy.engine import reflection

from utils import logging

logger = logging.getLogger(__name__)

def table_create_index(name, conn, dryrun=True):
    """ Creating indices on each column in the table """
    meta = MetaData(bind=conn)
    table = Table(name, meta, autoload=True)
    for col in table.columns:
        idx_name = '{tbl}_{col}_ix'.format(tbl=name, col=col.name)
        logger.info('Creating index for %s', idx_name)
        if not dryrun:
            Index(idx_name, col).create(conn)


def get_connection(url):
    """ Return an connection. """
    passwd = urllib.quote(getpass.getpass())
    if '@' in url:
        url_pw = url.replace('@', passwd + '@')
    else:
        url_pw = url.replace('://', '://{0}:{1}@'.format(getpass.getuser(), passwd))
    return create_engine(url_pw)


@click.command()
@click.option('--dryrun/--no-dryrun', default=True)
@click.argument('url')
@click.argument('tables', nargs=-1)
def console(url, tables, dryrun):
    """ Commandline """
    conn = get_connection(url)
    for tbl in tables:
        table_create_index(tbl, conn, dryrun)


if __name__ == "__main__":
    console()
