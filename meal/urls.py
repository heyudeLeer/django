"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^upload_zip$', views.upload_zip, name='upload_zip'),
    url(r'^upload_img$', views.upload_img, name='upload_img'),
    url(r'^start_train$', views.start_train, name='start_train'),
    url(r'^start_predict', views.start_predict, name='start_predict'),

    #url(r'^static/(?P<path>.*)', 'django.views.static.serve', {'document_root':'/home/heyude/PycharmProjects/mysite/meal/static'}),

]
