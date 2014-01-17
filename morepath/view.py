from morepath import generic
from .request import Request, Response
from reg import PredicateMatcher, Predicate
import json


class View(object):
    def __init__(self, func, render, permission):
        self.func = func
        self.render = render
        self.permission = permission

    def __call__(self, request, model):
        return self.func(request, model)


# XXX what happens if predicates is None for one registration
# but filled for another?
def register_view(registry, model, view, render=None, permission=None,
                  predicates=None):
    if permission is not None:
        # instantiate permission class so it can be looked up using reg
        permission = permission()
    registration = View(view, render, permission)
    if predicates is not None:
        matcher = registry.exact(generic.view, (Request, model))
        if matcher is None:
            predicate_info = registry.exact('predicate_info', ())
            predicate_info.sort()
            matcher = PredicateMatcher(
                [predicate for (order, predicate) in predicate_info])
        matcher.register(predicates, registration)
        registration = matcher
    registry.register(generic.view, (Request, model), registration)


def register_predicate(registry, name, order, default, index, calc):
    predicate_info = registry.exact('predicate_info', ())
    if predicate_info is None:
        predicate_info = []
        registry.register('predicate_info', (), predicate_info)
    predicate_info.append((order, Predicate(name, index, calc, default)))


def render_json(content):
    response = Response(json.dumps(content))
    response.content_type = 'application/json'
    return response


class RenderTemplate(object):
    def __init__(self, template_path):
        self.template_path = template_path

    def __call__(self, content):
        # have to do this here as have to wait for config to load
        if self.template is None:
            # XXX is compilation thread safe?
            self.template = self.compile_template(self.template_path)
        rendered = self.template(content)
        return render_html(rendered)


def render_html(content):
    response = Response(content)
    response.content_type = 'text/html'
    return response

def compile_template():
    pass
