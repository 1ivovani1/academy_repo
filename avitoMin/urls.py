from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from app1.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login',login_page),
    path('',main),
    path('register',register_page),
    path('logout',logout_page),
    path('user',user_page),
    path('plus_ad',add_ad),
    path('search_ads',search_ads)
] + static('media/', document_root = 'media/')
