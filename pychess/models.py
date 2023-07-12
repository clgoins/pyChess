from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    pass

class Game(models.Model):
    # roomCode is a code that players will use when joining a game
    roomCode = models.CharField(max_length=6, unique=True)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player1")
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player2", null=True, blank=True)
    isActive = models.BooleanField()
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner", null=True, blank=True)

class Move(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    moveNumber = models.IntegerField()
    
    # 'piece' will contain a code to refer to a specific piece on the board
    # P1, P2, P3.... P8 = pawns
    # R1, R2 = rooks
    # N1, N2 = knights,
    # B1, B2 = bishops,
    # K1 = king,
    # Q1 = queen
    # color of piece can be determined by the moveNumber
    piece = models.CharField(max_length=2)

    # rankFile is the position the piece is to move to. e.g. "A4" or "E7"
    rankFile = models.CharField(max_length=2)