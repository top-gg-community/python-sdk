from typing import TYPE_CHECKING
import sys
import os
import re


sys.path.insert(0, os.path.join(os.getcwd(), '..', 'topgg'))
sys.path.insert(0, os.path.abspath('..'))

if TYPE_CHECKING:
  from ..topgg.version import VERSION
else:
  from version import VERSION


project = 'topggpy'
author = 'null8626 & Top.gg'
copyright = ''

with open('../LICENSE', 'r') as f:
  copyright_match = re.search(rf'[\d\-]+(?:-[\d\-]+)? {author}', f.read())
  assert copyright_match is not None

  copyright = copyright_match.group()

version = VERSION
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx_reredirects']

autodoc_type_aliases = {
  'Listener': '~topgg.webhooks.Listener',
  'IntegrationCreateListener': '~topgg.webhooks.IntegrationCreateListener',
  'IntegrationDeleteListener': '~topgg.webhooks.IntegrationDeleteListener',
  'TestListener': '~topgg.webhooks.TestListener',
  'VoteCreateListener': '~topgg.webhooks.VoteCreateListener',
}

intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None),
  'aio': ('https://docs.aiohttp.org/en/stable/', None),
}

redirects = {
  'support-server': 'https://discord.gg/EYHTgJX',
  'repository': 'https://github.com/top-gg-community/python-sdk',
  'raw-api-reference': 'https://docs.top.gg/api/v1/introduction',
}

html_css_files = [
  'style.css',
  'https://fonts.googleapis.com/css2?family=Manrope:wght@200..800&display=swap',
]
html_js_files = ['script.js']
html_static_path = ['_static']
html_theme = 'furo'
html_title = project
html_favicon = '_static/favicon.ico'
