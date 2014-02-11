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


def test_subpath_url_parameters():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id, a):
            self.container_id = container_id
            self.a = a

    class Item(object):
        def __init__(self, parent, id, b):
            self.parent = parent
            self.id = id
            self.b = b

    @app.path(model=Container, path='{container_id}')
    def get_container(container_id, a):
        return Container(container_id, a)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id, b):
        return Item(base, id, b)

    @app.view(model=Item)
    def default(self, request):
        return "a: %s b: %s" % (self.parent.a, self.b)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/A/a?a=foo&b=bar')
    assert response.data == 'a: foo b: bar'

    response = c.get('/A/a')
    assert response.data == 'a: None b: None'

    response = c.get('/A/a/link?a=foo&b=bar')
    assert response.data == '/A/a?a=foo&b=bar'

    response = c.get('/A/a/link')
    assert response.data == '/A/a'


def test_subpath_url_parameters_converter():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id, a):
            self.container_id = container_id
            self.a = a

    class Item(object):
        def __init__(self, parent, id, b):
            self.parent = parent
            self.id = id
            self.b = b

    @app.path(model=Container, path='{container_id}')
    def get_container(container_id, a=0):
        return Container(container_id, a)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id, b=0):
        return Item(base, id, b)

    @app.view(model=Item)
    def default(self, request):
        return "a: %r b: %r" % (self.parent.a, self.b)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/A/a?a=1&b=2')
    assert response.data == 'a: 1 b: 2'

    response = c.get('/A/a')
    assert response.data == 'a: 0 b: 0'

    response = c.get('/A/a/link?a=1&b=2')
    assert response.data == '/A/a?a=1&b=2'

    response = c.get('/A/a/link')
    assert response.data == '/A/a?a=0&b=0'


@pytest.mark.xfail
def test_subpath_multiple_base():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id):
            self.container_id = container_id

    class ContainerA(Container):
        pass

    class ContainerB(Container):
        pass

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    @app.path(model=ContainerA, path='a/{container_id}')
    def get_container(container_id):
        return ContainerA(container_id)

    @app.path(model=ContainerB, path='b/{container_id}')
    def get_container(container_id):
        return ContainerB(container_id)

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

    response = c.get('a/T/t')
    assert response.data == 'Item t for parent T'

    response = c.get('b/T/t')
    assert response.data == 'Item t for parent T'

    response = c.get('a/T/t/link')
    assert response.data == 'a/T/t'

# required

# what if base variable same as sub variable? should be error

# what if container cannot be found, i.e get_base returns None

# what if base class is subclass of path registered

# variable 'base' is not a URL parameter
