from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Game, Bet, League, Membership
from .forms import BetForm, GameForm, LeagueForm, JoinLeagueForm
from django.contrib.auth import authenticate, login
from django.db.models import Count, Sum, Q
from django.shortcuts import redirect
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.models import User


def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)


def pending_games(request):
    if request.user.is_authenticated:

        current_user = request.user
        template = loader.get_template('pending_games.html')
        form = BetForm(request.POST or None)

        all_games = Game.objects.all()
        results = Game.objects.filter(home_goals__isnull=True)

        timenow = datetime.now()

        userbets = Bet.objects.filter(user_id=current_user.id)
        userpoints = userbets.aggregate(Sum('score'))
        games_without_bet_not_started = Game.objects.exclude(pk__in=[bet.game_id for bet in userbets]).filter(date__gt=datetime.now() + timedelta(hours=1))

        pending_games_counter = len(games_without_bet_not_started)

        if len(games_without_bet_not_started) == 0:
            messages.info(request, "You have no pending games")

        context = {
            'current_user': current_user,
            'all_games': games_without_bet_not_started,
            'form': form,
            'timenow': timenow,
            'userpoints': userpoints,
            'pending_games_counter': pending_games_counter
        }

        if request.method == 'POST':
            form = BetForm(request.POST)
            if form.is_valid():
                bet = form.save(commit=False)
                bet.game_id = request.POST.get('game_id')
                bet.user_id = current_user.id
                bet.bet = request.POST.get('bet')
                bet.save()
                return HttpResponseRedirect('')
            else:
                print(form.errors)

        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/polls/login')


def game_results(request, game_id):
    if request.user.is_staff:
        game = Game.objects.get(pk=game_id)
        next_game = game_id+1
        if request.method == 'POST':
            form = GameForm(request.POST, instance=game)
            if form.is_valid():
                form.save()
                return redirect('/polls/game_results/%s' % next_game)
        else:
            form = GameForm(instance=game)

        return render(request, 'game_results.html', {'form': form, 'game' : game, })
    else:
        messages.info(request, "You don't have access to this page")
        return HttpResponseRedirect('/polls')



def index(request):

    if request.user.is_authenticated:
        #latest_games_list = Bet.objects.order_by('-game_id')
        template = loader.get_template('index.html')
        current_user = request.user

        all_games = Game.objects.all()
        userbets = Bet.objects.filter(user_id=current_user.id).order_by('-game_id')
        userpoints = userbets.aggregate(Sum('score'))


        exact_scores = userbets.filter(score=2).aggregate(Count('score'))
        winner_predicted = userbets.filter(score=1).aggregate(Count('score'))
        wrong_bet = userbets.filter(score=0).aggregate(Count('score'))

        bets_join_games = userbets.select_related("game")

        userbets = Bet.objects.filter(user_id=current_user.id)
        games_without_bet_not_started = Game.objects.exclude(pk__in=[bet.game_id for bet in userbets]).filter(date__gt=datetime.now() + timedelta(hours=1))

        pending_games_counter = len(games_without_bet_not_started)


        color_wrongbet  = "#efefef"
        color_winner    = "#c7eae4"
        color_exact     = "#81ba75"

        context = {
            'userbets' : bets_join_games,
            'userpoints': userpoints,
            'current_user': current_user,
            'all_games': all_games,
            'exact_scores': exact_scores,
            'winner_predicted': winner_predicted,
            'wrong_bet' : wrong_bet,
            'pending_games_counter' : pending_games_counter,
            'color_wrongbet' : color_wrongbet,
            'color_winner': color_winner,
            'color_exact': color_exact,
        }

        return render(request, 'index.html', context)
    else:
        return HttpResponseRedirect('/polls/login')


def leaderboard(request):
    if request.user.is_authenticated:
        userpoints = Bet.objects.values('user_id', 'user__username').annotate(user_points=Sum('score')).order_by('-user_points')#select_related("user")

        template = loader.get_template('leaderboard.html')

        context = {
            'userpoints' : userpoints,
            'current_user': request.user,
        }

        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/polls/login')


def player(request, username):

    selected_player = User.objects.get(username=username)
    template = loader.get_template('player.html')


    all_games = Game.objects.all()
    userbets = Bet.objects.filter(user_id=selected_player.id)
    userpoints = userbets.aggregate(Sum('score'))

    exact_scores = userbets.filter(score=2).aggregate(Count('score'))
    winner_predicted = userbets.filter(score=1).aggregate(Count('score'))
    wrong_bet = userbets.filter(score=0).aggregate(Count('score'))

    bets_join_games = userbets.select_related("game")

    games_with_results = bets_join_games.filter(game__home_goals__isnull=False)

    userbets = Bet.objects.filter(user_id=selected_player.id)
    #games_with_results = Game.objects.filter(home_goals__isnull=False)
    games_without_bet_not_started = Game.objects.exclude(pk__in=[bet.game_id for bet in bets_join_games]).exclude(pk__in=[game.id for game in games_with_results]).filter(date__gt=datetime.now() + timedelta(hours=1))

    pending_games_counter = len(games_without_bet_not_started)

    color_wrongbet = "#efefef"
    color_winner = "#c7eae4"
    color_exact = "#81ba75"

    context = {
        'userbets': games_with_results,
        'userpoints': userpoints,
        'selected_player' : selected_player,
        'all_games': all_games,
        'exact_scores': exact_scores,
        'winner_predicted': winner_predicted,
        'wrong_bet': wrong_bet,
        'pending_games_counter': pending_games_counter,
        'color_wrongbet': color_wrongbet,
        'color_winner': color_winner,
        'color_exact': color_exact,
    }

    return render(request, 'player.html', context)


def active_bets(request): #wyswietla zaklady wszystkich graczy na mecze ktore sie ROZPOCZELY ale jeszcze nie maja wyniku

    all_bets = Bet.objects.all()
    #bets_join_games = all_bets.select_related("game").filter(game__date__lte=datetime.now()).filter(game__home_goals__isnull=True)

    all_games = Game.objects.all()
    games_join_bets = all_games.select_related("bet")

    timenow = datetime.now()

    template = loader.get_template('active_bets.html')

    context = {
        'bets_join_games': games_join_bets,
        'time': timenow,
    }

    return HttpResponse(template.render(context, request))


def create_league(request):
    template = loader.get_template('create_league.html')
    form = LeagueForm(request.POST or None)

    context = {'form' : form}

    if request.method == 'POST':
        form = LeagueForm(request.POST)
        if form.is_valid():
            print ('form is valid')

            league = form.save(commit=False)
            league.admin_id = request.user.id
            league.name = request.POST.get('name')
            league.save()
            messages.info(request, "Your league code is %s" % league.code)
            Membership.objects.create(user=request.user, league=league)
            return HttpResponseRedirect('')

        else:
            print(form.errors)

            # def save(self):
            #     new_league = League.objects.create_league(name=self.cleaned_data['name'], admin_id=request.user.id)
            #     new_user_to_league = UsersToLeagues.create_userstoleague(id=request.user.id, name=new_league.id)
            #     return new_league
            #     return new_user_to_league

    return HttpResponse(template.render(context, request))


def join_league(request):
    form = JoinLeagueForm(request.POST or None)

    template = loader.get_template('join_league.html')

    context = {
        'form': form,
    }

    if request.method == 'POST':
        leagues = League.objects.all()
        form = JoinLeagueForm(request.POST or None)
        if form.is_valid():
            search = form.cleaned_data['league_code']
            #code = request.POST.get('code')
            print (search)
            result = leagues.filter(code=search)
            ids = result.values('id')[0]
            league_id = ids['id']

            that_league = League.objects.get(code=search)
            messages.info(request, "You have successfully joined the %s league" % that_league.name)

            Membership.objects.create(user=request.user, league=that_league)

            return HttpResponseRedirect('')

    return HttpResponse(template.render(context, request))


def leagues(request):
    user = request.user
    users_leagues = user.league_set.all()

    template = loader.get_template('leagues.html')
    context = {
        'users_leagues' : users_leagues,
    }

    return HttpResponse(template.render(context, request))




def league_standings(request, league_id):
    league = League.objects.get(pk=league_id)
    league_members = league.members.all()

    members_bets = Bet.objects.filter(user_id__in=[member.id for member in league_members])

    userpoints = Bet.objects.values('user_id', 'user__username').filter(pk__in=[bet.id for bet in members_bets]).annotate(user_points=Sum('score')).order_by('-user_points')  # select_related("user")


    template = loader.get_template('league_standings.html')

    context = {
        'league': league,
        'league_members' : league_members,
        'userpoints': userpoints,
        'x': members_bets,
    }

    return HttpResponse(template.render(context, request))


def game_details(request, game_id):
    game = Game.objects.get(pk=game_id)
    user = request.user
    users_leagues = user.league_set.all()


    for league in users_leagues:
        league_members = league.members.all()
        members_bets = Bet.objects.filter(user_id__in=[member.id for member in league_members])

    template = loader.get_template('game_details.html')

    context = {
        'user' : user,
        'game': game,
        'league': league,
        'users_leagues' : users_leagues,
        'league_members': league_members,
        'members_bets': members_bets,
        'x': members_bets,
    }

    return HttpResponse(template.render(context, request))