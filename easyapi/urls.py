__author__ = 'Monte'
from django.conf.urls import url
import easyapi.views

urlpatterns = [
    url(r'login/$', easyapi.views.api_login_view, name="api-login"),
]
