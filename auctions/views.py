############################
#
#   AuctionEagle by Harold Hidalgo
#   for Hardvard University
#   CS50's Web Programming with Python and JavaScript
#
############################


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from flask import request as rq
import requests as rq
import datetime

from .models import User, Category, Listing, Bid, Comment, Watchlist


############################
#
#  Homepage, were all entries are shown
#
############################

def index(request):
    if request.method == "GET":
        # Fetch all listings from database
        data = Listing.objects.all()
        categories = Category.objects.all()

        #Render index.html page with all listings
        return render(request, "auctions/index.html", {
            "data": data,
            "categories": categories,
        })


############################
#
#  LOGIN VIEW  
#
############################

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


############################
#
#  LOGOUT VIEW
#
############################

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


############################
#
#  REGISTER FOR ACCOUNT
#
############################

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


############################
#
#  CREATE NEW LISTING
#
############################

@login_required(login_url='../login')
def new_listing(request):
    if request.method == "GET":

        categories = Category.objects.all()
        
        # Return new listing form
        return render(request, "auctions/new_listing.html", {
            "categories": categories,
        })

    if request.method == "POST":

        # Grab the data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        if request.POST["image_url"]:
            image_url = request.POST["image_url"]
        if request.POST["category"]:
            category_id = request.POST["category"]
        author = request.user.get_username()

        listing_category = Category.objects.get(id=category_id)
        listing_author = User.objects.get(username=author)

        # Create new Listing model
        NewListing = Listing(
            title = title,
            description = description,
            starting_bid = starting_bid,
            image_url = image_url,
            author = listing_author,
            category = listing_category
        )

        # Save new listing model
        NewListing.save()

        # Grab id from new listing model
        id = NewListing.identifier

        # Render listing page
        return HttpResponseRedirect(f"/listing/{id}")


############################
#
#  LISTING VIEW
#
############################

def listing(request, id):
        
        current_user = User.objects.get(username=request.user.get_username()) 
        data = Listing.objects.get(identifier=id)
        comments = Comment.objects.filter(listing=id)
        on_watchlist = Watchlist.objects.filter(listing=id, author=current_user).exists()
        categories = Category.objects.all()

        return render(request, "auctions/listing.html", {
            "current_user": current_user,
            "data": data,
            "on_watchlist": on_watchlist,
            "comments": comments,
            "categories": categories,
        })

############################
#
#  CATEGORY VIEW
#
############################

def category(request, id):
        
        current_user = User.objects.get(username=request.user.get_username())
        selected_category = Category.objects.get(id=id)
        data = Listing.objects.filter(category=selected_category.id)
        categories = Category.objects.all()

        return render(request, "auctions/index.html", {
            "current_user": current_user,
            "data": data,
            "category": True,
            "category_name": selected_category.name,
            "categories": categories,
        })


############################
#
#  MY LISTINGS VIEW
#
############################

@login_required(login_url='../login')
def mylistings(request):
    if request.method == "GET":
        author = User.objects.get(username=request.user.get_username())
        data = Listing.objects.filter(author=author)
        categories = Category.objects.all()

        return render(request, "auctions/my_listings.html", {
            "data": data,
            "categories": categories,
        })


############################
#
#  CLOSE AN AUCTION
#
############################

@login_required(login_url='../login')
def close_listing(request):

    item_id = request.GET["id"]
    Listing.objects.filter(identifier=item_id).update(listing_status=0)
    return HttpResponseRedirect(f"/listing/{item_id}")


############################
#
#  OPEN AUCTION
#
############################

@login_required(login_url='../login')
def open_listing(request):

    item_id = request.GET["id"]
    Listing.objects.filter(identifier=item_id).update(listing_status=1)
    return HttpResponseRedirect(f"/listing/{item_id}")


############################
#
#  ADD COMMENT
#
############################

@login_required(login_url='../login')
def new_comment(request):
    if request.method == "GET":
        id = request.GET["id"]
        return render(request, "auctions/new_comment.html", {
            "id": id
        })

    if request.method == "POST":

        item_id = request.POST["id"]

        current_listing = Listing.objects.get(identifier=item_id)
        current_user = request.user.get_username()
        author = User.objects.get(username=current_user)
        current_comment = request.POST["comment"]

        NewComment = Comment(
            listing = current_listing,
            text = current_comment,
            author = author,
        )

        NewComment.save()

        return HttpResponseRedirect(f"/listing/{item_id}")


############################
#
#  WATCHLIST FUNCTIONS (ADD, REMOVE, LOAD WL)
#
############################

@login_required(login_url='../login')
def watchlist(request):
    mode = request.GET["mode"]
    id = request.GET["id"]
    author = User.objects.get(username=request.user.get_username())

    if id == "all":
        current_id = 0
    else:
        current_id = Listing.objects.get(identifier=id)

    if mode == "add":
        NewWatchListItem = Watchlist(
            listing = current_id,
            author = author
        )

        NewWatchListItem.save()

    if mode == "remove":

        Watchlist.objects.filter(listing=current_id.identifier).delete()

    if mode == "view":

        watchlist = Watchlist.objects.filter(author=author)

        watchlist_items = []
        
        for item in watchlist:
            item_id = item.listing.identifier
            watchlist_items.extend(list(Listing.objects.filter(identifier=item_id)))
            
        
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist_items,
        } 
        )
    
    watchlist = Watchlist.objects.filter(author=author)

    watchlist_items = []
        
    for item in watchlist:
        item_id = item.listing.identifier
        watchlist_items.extend(list(Listing.objects.filter(identifier=item_id)))
            
        
    return HttpResponseRedirect("../watchlist?mode=view&id=all")


############################
#
#  PLACE BID
#
############################

@login_required(login_url='../login')
def bid(request, id):
    
    # Loads standard page to place bid
    if request.method == "GET":
        return render(request, "auctions/bid.html", {
            "id": id,
        })

    # Receives bid and processes it
    if request.method == "POST":
        
        # Check if the amount being submitted is a valid float number
        try:
            amount = float(request.POST["amount"])
        
        # If not, reload page with error message
        except ValueError:
            return render(request, "auctions/bid.html", {
            "id": id,
            "error": "The amount is not valid.",
            })
        
        listing_data = Listing.objects.get(identifier=id)

        if amount < listing_data.starting_bid:
            return render(request, "auctions/bid.html", {
            "id": id,
            "error": "Your bid must be higher than the starting bid.",
            })

        elif amount < listing_data.current_bid:
            return render(request, "auctions/bid.html", {
            "id": id,
            "error": "Your bid must be higher than the current highest bid.",
            })
        
        bidder = User.objects.get(username=request.user.get_username())
        listing_data = Listing.objects.get(identifier=id)

        if listing_data.author == bidder:
            return render(request, "auctions/bid.html", {
            "id": id,
            "error": "You cannot bid on your on auction.",
        })

        else:
            NewBid = Bid(
                listing = listing_data,
                bidder = bidder,
                amount = amount,
            )

            NewBid.save()
            
            # Update listing with new current bid and highest bidder
            Listing.objects.filter(identifier=id).update(current_bid=amount)
            Listing.objects.filter(identifier=id).update(current_winner=bidder)

            data = Listing.objects.get(identifier=id)
            comments = Comment.objects.filter(listing=id)
            on_watchlist = Watchlist.objects.filter(listing=id, author=User.objects.get(username=bidder)).exists()

            return render(request, "auctions/listing.html", {
                "current_user": bidder,
                "data": data,
                "on_watchlist": on_watchlist,
                "comments": comments,
                "bid_placed": "Bid successfully placed!",
            })