from django.conf.urls import url, include
from df_goods.views import *

urlpatterns = [
    url(r'^index/$', index),
    url(r'^list(\d+)_(\d+)_(\d+)/$', list),
    url(r'^(\d+)/$', detail),
]