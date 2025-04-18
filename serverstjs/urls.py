"""
URL configuration for serverstjs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from evaluador.views import *
from serverstjs.firestore import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('evaluar_codigo/', evaluar_codigo),
    path('free_chat/', free_chat, name='free_chat'),
    path('free_conversation/', free_conversation, name='free_conversation'),
    path('talking_chat/', talking_chat, name='talking_chat'),
    path('talking_chat_complete/', talking_chat_complete, name='talking_chat_complete'),
    path('registro/', register_user, name='registro'),
    path('login_google/', login_with_google, name='login_google'),
    path('login_user/', login_user, name='login_user'),
    path('get_progress/', get_progress, name='get_progress'),
    path('update_progress/', update_progress, name='update_progress'),
    path('verify_code/', verify_code, name='verify_code'),
    path('transcribir_audio/', transcribir_audio, name='transcribir_audio'),    
]
