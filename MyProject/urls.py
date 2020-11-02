from django.contrib import admin
from django.urls import path
from messenger.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('messages/', MessageList.as_view()),
]
