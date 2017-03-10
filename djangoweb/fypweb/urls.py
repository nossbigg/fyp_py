from django.conf.urls import url, include
from views import api, views

urlpatterns = [
    # Views
    url(r'^$', views.index),

    # Web Services
    url(r'api/', include([
        url(r'^test-get/', api.test),
    ])),
]
