from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    pass

class Game(models.Model):
    # roomCode is a code that players will use to join a game
    roomCode = models.CharField(max_length=6, unique=True, null=True, blank=True)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player1")
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player2", null=True, blank=True)
    isActive = models.BooleanField()
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner", null=True, blank=True)

    def __str__(self):
        return self.roomCode


class Move(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    moveNumber = models.IntegerField()
    pieceID = models.IntegerField()

    # rankFile is the position the piece is to move to. e.g. "A4" or "E7"
    rankFile = models.CharField(max_length=2)