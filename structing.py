#!/usr/bin/env python
"""
File: structing.py
Author: Wen Li
Email: spacelis@gmail.com
Github: http://github.com/spacelis
Description:
    This module provides tools for generating table structures for csv files.
"""

import re
from os.path import basename
from textwrap import dedent
import click
import messytables as mst
from jinja2 import Template
from utils import logging

logger = logging.getLogger(__name__)

DIGITS = re.compile(r'^\d+')

WHITESPACES = re.compile(r'\s+')

def mk_dbobj_name(prename, prepend='T'):
    """ Generate a proper name for database objects """
    if DIGITS.match(prename):
        return WHITESPACES.sub('_', prepend + prename.lower())
    return WHITESPACES.sub('_', prename.lower())


class Specification(object):

    """ The specification of the importing schema and mappings"""

    template = Template(dedent(
        '''
        from sqlalchemy import MetaData, Column, Table
        from sqlalchemy import Integer, String, Date, DateTime, Float, Boolean, Numeric

        meta = MetaData()

        {% for t in table_defs %}
        {{t}}

        {% endfor %}

        all_tables = [
            {% for t in table_defs -%}
            {{ t.table_name }}{{ ',' if not loop.last else '' }}
            {%- endfor %}
        ]
        all_files = [
            {% for t in table_defs -%}
            ('{{ t.file_name }}', {{ t.render_headers() }}){{ ',' if not loop.last else '' }}
            {%- endfor %}
        ]
        '''
    ))

    def __init__(self, table_defs):
        """ Make a Specification

        :table_defs: TODO

        """
        self.table_defs = table_defs

    def __str__(self):
        """ Render specification
        :returns: TODO

        """
        return Specification.template.render({
            'table_defs': self.table_defs
        })



class ColumnDef(object):

    """Column definitions"""

    TYPEMAPPING = {
        'Integer':  'Integer',
        'String':   'String',
        'Boolean':  'Boolean',
        'Bool':  'Boolean',
        'Date':     'Date',
        'Float':    'Float',
        'DateTime': 'DateTime',
        'Decimal': 'Numeric',

    }


    template = Template('''Column('{{ name }}', {{ type }})''')


    def __init__(self, header, csvtype):
        """ Make a column definition

        :header: The name of the column
        :csvtype: The type guessed by messytables

        """
        self.header = header
        self.name = mk_dbobj_name(header, 'C')
        self.type = ColumnDef.TYPEMAPPING[str(csvtype)]

    def __str__(self):
        """ Render column definition
        :returns: a rendering context for column template

        """
        return ColumnDef.template.render({
            'name': self.name,
            'type': self.type
        })


class TableDef(object):

    """Table definitions"""

    template = Template(dedent(
        '''
        {{ table_name }} = Table('{{ table_name }}', meta,
                    {% for coldef in column_defs -%}
                    {{ coldef }}{{ '' if loop.last else ',' }}
                    {% endfor %}
                    )
        '''
    ))

    def __init__(self, table_name, column_defs, file_name):
        """ Make a table definition

        :table_name: TODO
        :column_defs: TODO

        """
        self.table_name = table_name
        self.column_defs = column_defs
        self.file_name = file_name

    def render_headers(self):
        """ Return new headers for loading
        :returns: TODO

        """
        return repr([c.name for c in self.column_defs])

    def __str__(self):
        """ Render table definition
        :returns: a rendered table definition

        """
        return TableDef.template.render({
            'table_name': self.table_name,
            'column_defs': self.column_defs
        })


class CSVFile(object):

    """A structure containing metadata of a csv file"""

    def __init__(self, file_name, nullsyms=('',)):
        """TODO: to be defined1. """
        self.file_name = file_name
        self.fin = None
        self.row_set = None
        self.headers = None
        self.offset = None
        self.types = None

    def guess_structure(self):
        """TODO: Docstring for start.
        :returns: TODO

        """
        with open(self.file_name, 'rb') as fin:
            row_set = mst.CSVRowSet('', fin)
            self.offset, self.headers = mst.headers_guess(row_set.sample)

    def _prepare(self):
        """TODO: Docstring for prepare.

        :arg1: TODO
        :returns: TODO

        """
        assert self.row_set, 'The row_set is not ready.'
        if self.headers is None:
            raise ValueError('')
        self.row_set.register_processor(mst.headers_processor(self.headers))
        self.row_set.register_processor(mst.offset_processor(self.offset + 1))

        self.types = mst.type_guess(self.row_set.sample, strict=True)
        self.row_set.register_processor(mst.types_processor(self.types))

        logger.debug("File: %s", self.file_name)
        logger.debug("Header: %s", self.headers)
        logger.debug("Types: %s", self.types)
        return self

    def close(self):
        """ Close the csv file
        :returns: TODO

        """
        self.fin.close()

    def __enter__(self):
        """ Context enter
        :returns: TODO

        """
        if self.headers is None:
            self.guess_structure()
        self.fin = open(self.file_name, 'rb')
        self.row_set = mst.CSVRowSet('', self.fin)
        self._prepare()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Context exit

        :exc_type: TODO
        :exc_val: TODO
        :exc_tb: TODO
        :returns: TODO

        """
        self.close()


def table_schema(file_name):
    """ Generate table schema for the csv file

    """
    with CSVFile(file_name) as csvfile:
        table_name = mk_dbobj_name(basename(file_name).split('.')[0], 'T')
        column_defs = [ColumnDef(h, t) for h, t in zip(csvfile.headers, csvfile.types)]
        table_def = TableDef(table_name, column_defs, file_name)
        logger.debug('Table Def: %s', table_def)
        return table_def


def specification(file_names):
    """ Generate a python skeliton script for importing specification

    :file_names: TODO
    :returns: TODO

    """
    table_defs = [table_schema(f) for f in file_names]
    spec = Specification(table_defs)
    logger.debug('Spec: %s', spec)
    return spec


@click.command()
@click.argument('output', nargs=1, type=click.Path(exists=False))
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def make_schema(output, files):
    """ Commandline for exporting a schema based on the given csv."""
    with open(output, 'w') as fout:
        fout.write(str(specification(files)))


if __name__ == "__main__":
    make_schema()
