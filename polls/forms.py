from django import forms
from django.forms import ModelForm
from .models import Game,Bet, League
from django.db import transaction


class BetForm(forms.ModelForm):
    class Meta:
        model  = Bet
        fields = ['home_goals', 'away_goals']
        labels = { 'home_goals': '',
                   'away_goals': ''}


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('home_goals', 'away_goals')
        labels = {'home_goals': '',
                  'away_goals': ''}

    @transaction.atomic
    def save(self):
        game = super().save(commit=True)
        for bet in game.bet_set.all():
            if bet.home_goals == game.home_goals and bet.away_goals == game.away_goals:
                bet.score = 2
            elif game.home_goals< game.away_goals and bet.home_goals< bet.away_goals:
                bet.score = 1
            elif game.home_goals > game.away_goals and bet.home_goals > bet.away_goals:
                bet.score = 1
            elif game.home_goals == game.away_goals and bet.home_goals == bet.away_goals:
                bet.score = 1
            else:
                bet.score = 0
            bet.save()
        return game


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['name']
        labels = {'name' : 'League name'}


class JoinLeagueForm(forms.Form):
    league_code = forms.CharField(label="League code", max_length=32)


