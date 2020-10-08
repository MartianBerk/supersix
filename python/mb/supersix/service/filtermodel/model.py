from collections import namedtuple


Column = namedtuple("Column", "column,value")
Filter = namedtuple("Filter", "column,operator,value")
