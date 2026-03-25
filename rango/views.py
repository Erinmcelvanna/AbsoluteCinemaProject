from django.shortcuts import render

def index(request):
    return render(request, 'rango/index.html')

def register_view(request):
    return render(request, 'rango/register.html')

def login_view(request):
    return render(request, 'rango/login.html')

def discover(request):
    movies = [
        "Sinners",
        "Conclave",
        "The Meg",
        "Fresh",
        "Twisters",
        "The Housemaid",
        "Now You See Me",
        "Mirror Mirror"
    ]
    return render(request, 'rango/discover.html', {'movies': movies})

def profile(request):
    favourite_movies = [
        "Sinners",
        "Taken",
        "Panic",
        "Mirror Mirror"
    ]

    recently_watched = [
        "The Meg",
        "Fresh",
        "Twisters",
        "Now You See Me"
    ]

    context = {
        'favourite_movies': favourite_movies,
        'recently_watched': recently_watched,
    }

    return render(request, 'rango/profile.html', context)

def movie_detail(request):
    return render(request, 'rango/movie_detail.html')