from django.conf.urls import url
from django.conf.urls import include
from django.urls import path
from . import views

urlpatterns = [

    url(r'^', include('django.contrib.auth.urls')),

    url(r'^accounts/', include('registration.backends.default.urls')),

    #ex: /polls/
    url(r'^$', views.index, name='index'),

    # pending_games
    url(r'^pending_games/$', views.pending_games, name='pending_games'),

    path('<int:game_id>/game_results', views.game_results, name='game_results'),

    path('game_results/<int:game_id>', views.game_results, name='game_results1'),

    url('leaderboard', views.leaderboard, name='leaderboard'),

    url(r'^user/(?P<username>\w+)/$',  views.player, name='player'),

    url('active_bets', views.active_bets, name='active_bets'),

    url('create_league', views.create_league, name='create_league'),

    url('join_league', views.join_league, name='join_league'),

    url('leagues$', views.leagues, name='leagues'),

    path('leagues/standings/<int:league_id>',  views.league_standings, name='league_standings'),

    path('game_details/<int:game_id>', views.game_details, name='game_details')

        ]