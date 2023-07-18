from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    pass

class Game(models.Model):
    # roomCode is a code that players will use when joining a game
    roomCode = models.CharField(max_length=6, unique=True, null=True, blank=True)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player1")
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player2", null=True, blank=True)
    isActive = models.BooleanField()
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner", null=True, blank=True)

class Move(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    moveNumber = models.IntegerField()
    
    # 'piece' will contain a 3 character code to refer to a specific piece on the board
    # First character will be 'l' or 'd' to refer to light or dark pieces
    # Second character will be 'p', 'r', 'n', 'b, 'q', or 'k' to refer to the class of piece
    # (pawn, rook, knight, bishop, queen, or king, respectively)
    # Third character is a number to refer to WHICH piece. 1-8 for pawns, 1-2 for rooks knights and bishops, or just 1 for king and queen
    # Pieces will be numbered from left to right at the start of a game
    piece = models.CharField(max_length=3)

    # rankFile is the position the piece is to move to. e.g. "A4" or "E7"
    rankFile = models.CharField(max_length=2)