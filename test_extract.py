import re

html = open('rif/help/index.html', encoding='utf-8').read()
script = re.search(r'<script>(.*?)</script>', html, re.DOTALL).group(1)
open('test.js', 'w', encoding='utf-8').write(script)
