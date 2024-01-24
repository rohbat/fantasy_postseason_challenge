from flask import request, redirect
from urllib.parse import urlparse, urlunparse

def register_blueprints(app):
    from . import auth, dashboard
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)

    @app.before_request
    def redirect_subdomains():
        """Redirect non-www and www requests to football.<domain>"""
        urlparts = urlparse(request.url)
        if urlparts.netloc in ['fantasypostseasonchallenge.com', 'www.fantasypostseasonchallenge.com']:
            urlparts = urlparts._replace(netloc='football.fantasypostseasonchallenge.com')
            return redirect(urlunparse(urlparts), code=301)