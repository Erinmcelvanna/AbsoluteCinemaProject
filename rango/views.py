from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Movie, Favourite
from django.http import JsonResponse
import requests

TMDB_API_KEY ="f0efa2032b75218ca0109f65455e33b3"
def index(request):
    url = "https://api.themoviedb.org/3/trending/all/week"
    params = {
        "api_key": "f0efa2032b75218ca0109f65455e33b3"
    }

    response = requests.get(url, params=params)
    data = response.json()
    print("STATUS CODE:", response.status_code, flush=True)
    print("NUMBER OF RESULTS:", len(data.get("results", [])), flush=True)
    trending_titles = data.get("results", [])[:10]

    context = {
        "trending_titles": trending_titles
    }

    return render(request, 'rango/index.html',context)

def home(request):
    api_key = "f0efa2032b75218ca0109f65455e33b3"

    # Trending
    trending = requests.get(
        "https://api.themoviedb.org/3/trending/all/week",
        params={"api_key": api_key}
    ).json().get("results", [])
    trending = [item for item in trending if item.get("media_type") in ["movie", "tv"]]
    # Popular Movies
    movies = requests.get(
        "https://api.themoviedb.org/3/movie/popular",
        params={"api_key": api_key}
    ).json().get("results", [])

    # Popular TV
    tv = requests.get(
        "https://api.themoviedb.org/3/tv/popular",
        params={"api_key": api_key}
    ).json().get("results", [])

    return render(request, "rango/home.html", {
        "trending": trending[:10],
        "movies": movies[:10],
        "tv": tv[:10],
    })

def register_view(request):

    context = {}

    if request.method == 'POST':

        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not email or not username or not password1 or not password2:
            context['error'] = 'Please fill in all fields.'

        elif password1 != password2:
            context['error'] = 'Passwords do not match.'

        elif User.objects.filter(username=username).exists():
            context['error'] = 'Username already exists.'

        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )

            UserProfile.objects.get_or_create(user=user)

            login(request, user)

            return redirect('rango:profile')

    return render(request, 'rango/register.html', context)


def login_view(request):

    context = {}

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:

            login(request, user)

            return redirect('rango:profile')

        else:
            context['error'] = 'Invalid username or password.'

    return render(request, 'rango/login.html', context)


def logout_view(request):

    logout(request)

    return redirect('rango:index')




def discover(request):
    query = request.GET.get('q', '').strip()
    media_type_filter = request.GET.get('type', '').strip()

    if query:
        url = "https://api.themoviedb.org/3/search/multi"
        params = {
            "api_key": "f0efa2032b75218ca0109f65455e33b3",
            "query": query
        }
    else:
        url = "https://api.themoviedb.org/3/trending/all/week"
        params = {
            "api_key": "f0efa2032b75218ca0109f65455e33b3"
        }

    response = requests.get(url, params=params)
    data = response.json()

    movies = data.get("results", [])
    movies = [item for item in movies if item.get("media_type") in ["movie", "tv"]]

    if media_type_filter in ["movie", "tv"]:
        movies = [item for item in movies if item.get("media_type") == media_type_filter]

    return render(request, "rango/discover.html", {
        "movies": movies
    })
@login_required
def profile(request):

    if request.user.is_authenticated:

        favourite_movies = list(
            Movie.objects.filter(favourited_by__user=request.user)
            .distinct()
            .values_list('title', flat=True)
        )

        recently_watched = list(
            Movie.objects.filter(watch_histories__user=request.user)
            .distinct()
            .values_list('title', flat=True)[:4]
        )

    else:

        favourite_movies = []
        recently_watched = []

    context = {
        'favourite_movies': favourite_movies,
        'recently_watched': recently_watched,
    }

    return render(request, 'rango/profile.html', context)



def movie_detail(request,media_type ,tmdb_id):
    TMDB_API_KEY = "f0efa2032b75218ca0109f65455e33b3"
    if media_type == "tv":
            url = f"https://api.themoviedb.org/3/tv/{tmdb_id}"
    else:
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"

    params = {
            "api_key":"f0efa2032b75218ca0109f65455e33b3"
        }

    response = requests.get(url, params=params)
    movie = response.json()

    return render(request, "rango/movieDetail.html", {
        "movie": movie,
        "media_type": media_type
    })

@login_required
def add_favourite(request, movie_id):
    if request.method == "POST":
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "Movie not found"})

        Favourite.objects.get_or_create(
            user=request.user,
            movie=movie
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "failed"})