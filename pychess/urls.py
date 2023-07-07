from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.loginView, name="login"),
    path("logout", views.logoutView, name="logout"),
    path("register", views.register, name="register"),
    path("play", views.newGame, name="newGame"),
    path("play/local", views.localGame, name="localGame"),
    path("play/network", views.networkGame, name="networkGame")
    
]