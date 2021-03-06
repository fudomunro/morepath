from .path import register_path, get_arguments, SPECIAL_ARGUMENTS
from .reify import reify
from reg import mapply


class Mount(object):
    def __init__(self, app, context_factory, variables):
        self.app = app
        self.context_factory = context_factory
        self.variables = variables

    def create_context(self):
        return mapply(self.context_factory, **self.variables)

    def __repr__(self):
        variable_info = ', '.join(["%s=%r" % t for t in
                                   sorted(self.variables.items())])
        result = '<morepath.Mount of %s' % repr(self.app)
        if variable_info:
            result += ' with variables: %s>' % variable_info
        else:
            result += '>'
        return result

    @reify
    def lookup(self):
        return self.app.lookup

    def set_implicit(self):
        self.app.set_implicit()

    def __call__(self, environ, start_response):
        request = self.app.request(environ)
        request.mounts.append(self)
        response = self.app.publish(request)
        return response(environ, start_response)

    @reify
    def parent(self):
        return self.variables.get('parent')

    def child(self, app, **context):
        factory = self.app._mounted.get(app)
        if factory is None:
            return None
        if 'parent' not in context:
            context['parent'] = self
        mounted = factory(**context)
        if mounted.create_context() is None:
            return None
        return mounted


def register_mount(base_app, app, path, converters, required, get_converters,
                   context_factory):
    # specific class as we want a different one for each mount
    class SpecificMount(Mount):
        def __init__(self, **kw):
            super(SpecificMount, self).__init__(app, context_factory, kw)
    # need to construct argument info from context_factory, not SpecificMount
    arguments = get_arguments(context_factory, SPECIAL_ARGUMENTS)
    register_path(base_app, SpecificMount, path, lambda m: m.variables,
                  converters, required, get_converters,
                  SpecificMount, arguments=arguments)
    register_mounted(base_app, app, SpecificMount)


def register_mounted(base_app, app, model_factory):
    base_app._mounted[app] = model_factory
