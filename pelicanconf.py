AUTHOR = 'Matt Bramlage'
SITENAME = 'Stytch Getting Started'
SITEURL = ""

PATH = "content"

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Stytch", "https://stytch.com"),
    ("Github", "https://github.com/praecipula")
)

THEME = "/Users/matt/Development/pelican-themes/bootstrap"
JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
