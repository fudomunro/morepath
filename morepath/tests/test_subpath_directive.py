import morepath
from morepath import setup
from morepath.request import Response
from morepath.error import DirectiveReportError

from werkzeug.test import Client
import pytest


def test_subpath():
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

# combine variables, converters, required

# what if container cannot be found, i.e get_base returns None

# what if base class is subclass of path registered
