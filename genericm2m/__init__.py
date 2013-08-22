VERSION = (0, 2, 1)
from sys import version_info
is_3 = version_info[0] == 3

if is_3:
    unicode = str
    str = bytes
else:
    unicode = unicode
    str = str
