from django.contrib import admin
from django.urls import path, re_path
from service import views
from django.conf import settings

from django.views.static import serve 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/main', views.CSVMainView.as_view()),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
