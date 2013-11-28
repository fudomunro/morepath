from .publish import publish, Mount
from .request import Request
from .traject import Traject
from .config import Configurable
from reg import ClassRegistry, Lookup, ChainClassLookup, CachingClassLookup
import venusian
from werkzeug.serving import run_simple

def callback(scanner, name, obj):
    scanner.config.configurable(obj)


class AppBase(Configurable, ClassRegistry):
    # XXX have a way to define parameters for app here
    def __init__(self, name='', extends=None):
        ClassRegistry.__init__(self)
        Configurable.__init__(self, extends)
        self.name = name
        self.traject = Traject()
        # allow being scanned by venusian
        venusian.attach(self, callback)

    def __repr__(self):
        return '<morepath.App %r>' % self.name

    def clear(self):
        ClassRegistry.clear(self)
        Configurable.clear(self)
        self.traject = Traject()

    def lookup(self):
        # XXX instead of a separate cache we could put caching in here
        return app_lookup_cache.get(self)

    def request(self, environ):
        request = Request(environ)
        request.lookup = self.lookup()
        request.unconsumed = []
        return request

    def context(self, **kw):
        def wsgi(environ, start_response):
            return self(environ, start_response, context=kw)
        return wsgi

    def mounted(self, context=None):
        context = context or {}
        return Mount(self, lambda: context, {})

    def __call__(self, environ, start_response, context=None):
        request = self.request(environ)
        response = publish(request, self.mounted(context))
        return response(environ, start_response)

    def run(self, host=None, port=None, **options):
        if host is None:
            host = '127.0.0.1'
        if port is None:
            port = 5000
        run_simple(host, port, self, **options)


class App(AppBase):
    def __init__(self, name='', extends=None):
        if not extends:
            extends = [global_app]
        super(App, self).__init__(name, extends)
        # XXX why does this need to be repeated?
        venusian.attach(self, callback)


class AppLookupCache(object):
    def __init__(self):
        self.cache = {}

    def get(self, app):
        lookup = self.cache.get(app)
        if lookup is not None:
            return lookup
        caching_class_lookup = CachingClassLookup(app)
        result = self.cache[app] = Lookup(caching_class_lookup)
        return result

global_app = AppBase('global_app')

app_lookup_cache = AppLookupCache()
