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
        from sqlalchemy import Integer, String, Date, DateTime, Float, Boolean
        import messytables.types
        from structing import CSVFile

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
            {{ t.csvfile }}{{ ',' if not loop.last else '' }}
            {% endfor %}
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

    def __init__(self, table_name, column_defs, csvfile):
        """ Make a table definition

        :table_name: TODO
        :column_defs: TODO

        """
        self.table_name = table_name
        self.column_defs = column_defs
        self.csvfile = csvfile
        self.csvfile.headers = self.colnames()

    def colnames(self):
        """ Return new headers for loading
        :returns: TODO

        """
        return [c.name for c in self.column_defs]

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

    def __init__(self, file_name, headers, types, offset):
        """TODO: to be defined1. """
        self.file_name = file_name
        self.fin = None
        self.row_set = None
        self.offset = offset
        self.headers = headers
        self.types = types

    @classmethod
    def from_file(cls, file_name):
        """TODO: Docstring for start.
        :returns: TODO

        """
        with open(file_name, 'rb') as fin:
            row_set = mst.CSVRowSet('', fin)
            offset, headers = mst.headers_guess(row_set.sample)
            row_set.register_processor(mst.headers_processor(headers))
            row_set.register_processor(mst.offset_processor(offset + 1))
            types = mst.type_guess(row_set.sample, strict=True)
            return cls(file_name, headers, types, offset)

    @classmethod
    def from_structure(cls, file_name, structure, offset=0):
        headers, types = zip(*structure)
        return cls(file_name, headers, types, offset)

    def _prepare(self):
        """TODO: Docstring for prepare.

        :arg1: TODO
        :returns: TODO

        """
        self.row_set.register_processor(mst.headers_processor(self.headers))
        self.row_set.register_processor(mst.offset_processor(self.offset + 1))
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

    def __str__(self, headers=None):
        """ Serializing
        :returns: TODO

        """
        if headers is None:
            headers = self.headers
        return """CSVFile.from_structure({0}, {1}, {2})""".format(
            repr(self.file_name),
            '[\n        {0}]'.format(',\n        '.join(
                ['({0}, {1}.{2})'.format(repr(h), t.__module__, t.__class__.__name__)
                 for h, t in zip(headers, self.types)])),
            repr(self.offset)
            )


def table_schema(file_name):
    """ Generate table schema for the csv file

    """
    with CSVFile.from_file(file_name) as csvfile:
        table_name = mk_dbobj_name(basename(file_name).split('.')[0], 'T')
        column_defs = [ColumnDef(h, t) for h, t in zip(csvfile.headers, csvfile.types)]
        table_def = TableDef(table_name, column_defs, csvfile)
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
