from django.db import models
from django.contrib.auth.models import User
import uuid


class Game(models.Model):
    home_team = models.CharField(max_length=200)
    away_team = models.CharField(max_length=200)
    home_goals = models.IntegerField(default=None, null=True)
    away_goals = models.IntegerField(default=None, null=True)
    date = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)


class Bet(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    home_goals = models.IntegerField()
    away_goals = models.IntegerField()
    score = models.IntegerField(default=None, null=True)


class League(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name  = models.CharField(max_length=50)
    code  = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='league_admin')
    members = models.ManyToManyField(User, through='Membership')


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)