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
    path("spectate", views.spectate, name="spectate"),


    # API ==============
    path("check", views.checkMoves, name="checkMoves"),
    path("gameState", views.getGameState, name="gameState"),
    path("move", views.submitMove, name="submitMove"),
    path("win", views.checkForWinCondition, name="checkForWinCondition"),
    path("moveList", views.getMoveList, name="moveList")
    
]