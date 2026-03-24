from django.contrib import admin
from .models import UserProfile, Movie, Rating, Review, Favourite, WatchHistory

admin.site.register(UserProfile)
admin.site.register(Movie)
admin.site.register(Rating)
admin.site.register(Review)
admin.site.register(Favourite)
admin.site.register(WatchHistory)