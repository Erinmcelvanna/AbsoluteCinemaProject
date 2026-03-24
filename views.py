def test_movie(request):
    movie = {
        'id': 1,
        'title': 'Test Movie',
        'year': 2024,
        'genre': 'Drama',
        'description': 'This is just a test movie so you can see the page.',
        'poster_url': 'https://via.placeholder.com/300x450'
    }

    reviews = [
        {'user': {'username': 'erin'}, 'rating': 5, 'comment': 'Love this'},
        {'user': {'username': 'test'}, 'rating': 3, 'comment': 'It was okay'}
    ]

    return render(request, 'rango/movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'average_rating': 4.0
    })