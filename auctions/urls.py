from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("category/<int:id>", views.category, name="category"),
    path("bid/<int:id>", views.bid, name="bid"),
    path("mylistings", views.mylistings, name="my_listings"),
    path("new_comment", views.new_comment, name="new_comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close_listing", views.close_listing, name="close_listing"),
    path("open_listing", views.open_listing, name="open_listing"),
]
