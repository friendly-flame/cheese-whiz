# System Regular Expressions

import re


qi = re.compile(r'((?:[0-9](?:[\./][0-9]+)?) (?:.*?)) \b(.*)')

preparation = re.compile(r'\b([a-z]*ed)\b')

lolnum = re.compile(r'[0-9]')