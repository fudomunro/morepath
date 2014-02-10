import morepath
from morepath import setup
from morepath.request import Response
from morepath.error import DirectiveReportError

from werkzeug.test import Client
import pytest


def test_subpath_implicit_variables():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id):
            self.container_id = container_id

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    @app.path(model=Container, path='{container_id}')
    def get_container(container_id):
        return Container(container_id)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id):
        return Item(base, id)

    @app.view(model=Item)
    def default(self, request):
        return "Item %s for parent %s" % (self.id, self.parent.container_id)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/A/a')
    assert response.data == 'Item a for parent A'

    response = c.get('/B/a')
    assert response.data == 'Item a for parent B'

    response = c.get('/A/a/link')
    assert response.data == '/A/a'

    response = c.get('/B/a/link')
    assert response.data == '/B/a'


def test_subpath_explicit_variables():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, id):
            self.id = id

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    @app.path(model=Container, path='{container_id}',
              variables=lambda m: dict(container_id=m.id))
    def get_container(container_id):
        return Container(container_id)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent,
                 variables=lambda m: dict(id=m.id))
    def get_item(base, id):
        return Item(base, id)

    @app.view(model=Item)
    def default(self, request):
        return "Item %s for parent %s" % (self.id, self.parent.id)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/A/a')
    assert response.data == 'Item a for parent A'

    response = c.get('/B/a')
    assert response.data == 'Item a for parent B'

    response = c.get('/A/a/link')
    assert response.data == '/A/a'

    response = c.get('/B/a/link')
    assert response.data == '/B/a'


def test_subpath_converters():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id):
            self.container_id = container_id

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    @app.path(model=Container, path='{container_id}')
    def get_container(container_id=0):
        return Container(container_id)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id=0):
        return Item(base, id)

    @app.view(model=Item)
    def default(self, request):
        return "Item %r for parent %r" % (self.id, self.parent.container_id)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/1/2')
    assert response.data == 'Item 2 for parent 1'

    response = c.get('/2/1')
    assert response.data == 'Item 1 for parent 2'

    response = c.get('/1/2/link')
    assert response.data == '/1/2'

    response = c.get('/2/1/link')
    assert response.data == '/2/1'

# converters, required

# URL parameters combined

# what if base variable same as sub variable? should be error

# what if container cannot be found, i.e get_base returns None

# what if base class is subclass of path registered
