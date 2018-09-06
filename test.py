import re

text = '<@U07JFSV7X|james>'

if any(re.findall(r'<@U', text, re.IGNORECASE)):
    print('success')
