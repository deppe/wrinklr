"""
WSGI config for wrinklr_django project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""
from django.core.wsgi import get_wsgi_application
from dj_static import Cling
import sys

#uncomment to redirect stderr to stdout
#sys.stdout = sys.stderr

application = Cling(get_wsgi_application())
