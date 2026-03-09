"""
URL configuration for users App from LITRevu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path

from .views import (
    IndexView,
    LoginView,
    LogoutView,
    RegisterView,
    FluxView,
    PostsView,
    AbonnementsView,
)

app_name = 'users'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('flux/', FluxView.as_view(), name='flux'),
    path('posts/', PostsView.as_view(), name='posts'),
    path('abonnements/', AbonnementsView.as_view(), name='abonnements'),
]