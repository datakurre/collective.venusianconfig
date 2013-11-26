from collective.venusianconfig import configure
from collective.venusianconfig import scan

from venusianconfigdemo import views
from venusianconfigdemo import adapters

configure.browser.resourceDirectory(
    name='venusianconfigdemo',
    directory='static'
)

scan(views)
scan(adapters)

configure.browser.page(
    name='hello-world-template',
    for_='*',
    template='templates/hello_world.pt',
    permission='zope2.View',
)
