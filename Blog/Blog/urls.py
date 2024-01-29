from django.contrib import admin
from django.urls import path , include

admin.site.site_header = 'Blog Administration'





urlpatterns = [
    path('admin/', admin.site.urls),
    path('' , include('blog.urls' , namespace='blog')),
]
