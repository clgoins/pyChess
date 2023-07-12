from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.loginView, name="login"),
    path("logout", views.logoutView, name="logout"),
    path("register", views.register, name="register"),
    path("play", views.play, name="play"),
    path("play/local", views.localGame, name="localGame"),
    path("play/network", views.networkGame, name="networkGame"),
    path("review", views.review, name="review"),
    path("spectate", views.spectate, name="spectate")
    
]