from web import app
#enables trailing and non-trailing slash routes
app.url_map.strict_slashes = False