VERSION = (0, 3, 1)
from sys import version_info
PY3 = version_info[0] == 3

if PY3:
    unicode = str
    str = bytes
else:
    unicode = unicode
    str = str
