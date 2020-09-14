import datetime

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Watchlist, Bids, Comments


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.filter(active=True)
    })


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


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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


def create(request):
    if request.method == "POST":
        username = request.user.username
        title = request.POST["title"]
        bid = request.POST["bid"]
        description = request.POST["description"]
        url = request.POST["url"]
        category = request.POST["category"]

        if category == "":
            category = "No category listed"
        
        Auction.objects.create(username=username, title=title, price=bid, description=description,
                               creation_date=datetime.datetime.now(), photo=url, category=category)
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html")


def listings(request, listing_id):
    listing = Auction.objects.get(id=listing_id)
    amount_of_bids = Bids.objects.filter(listing=listing).count()
    current_bid = Bids.objects.filter(listing=listing).order_by('bid_price').last()
    my_watchlist = Watchlist.objects.filter(username=request.user.username)    
    my_watchlist_listings = [watchlist_object.listing for watchlist_object in my_watchlist]    
    
    # Forms
    if request.method == "POST":
        # Bid form
        if "Bid" in request.POST:            
            bid_price = request.POST["bid_price"]
            starting_bid_price = listing.price 
            other_bids_prices = Bids.objects.filter(listing=listing).values_list('bid_price', flat=True)

            # Displaying errors 
            if float(bid_price) < float(starting_bid_price):                
                return render(request, "auctions/listings_logged_in.html", {
                        "message": "Bid price is smaller than starting bid price.",                        
                        "listing": listing,
                        "watchlist_listings": my_watchlist_listings,
                        "amount_of_bids": amount_of_bids,
                        "current_bid": current_bid
                }) 

            if other_bids_prices and float(bid_price) <= float(max(other_bids_prices)):                
                return render(request, "auctions/listings_logged_in.html", {
                    "message": "Bid price is smaller than other bids.",                    
                    "listing": listing,
                    "watchlist_listings": my_watchlist_listings,
                    "amount_of_bids": amount_of_bids,
                    "current_bid": current_bid
            })        
            # Displaying errors end

            Bids.objects.create(listing=listing,
                                username=request.user.username, bid_price=bid_price)
            return HttpResponseRedirect(reverse("listings", args=[listing_id]))
        # Comment form
        elif "Comment" in request.POST:
            comment = request.POST["comment"]
            Comments.objects.create(listing=listing,
                                    username=request.user.username, date=datetime.datetime.now(), 
                                    text=comment)
            return HttpResponseRedirect(reverse("listings", args=[listing_id]))
    # Forms end

    if request.user.is_authenticated:        
        if request.user.username == listing.username:
            # ability to “close” the auction...
            return render(request, "auctions/listings_logged_in.html", {
            "listing": listing,            
            "watchlist_listings": my_watchlist_listings,
            "can_close_listing": True,
            "amount_of_bids": amount_of_bids,
            "current_bid": current_bid,
            "comments": Comments.objects.filter(listing=listing)
        })

        return render(request, "auctions/listings_logged_in.html", {
            "listing": listing,            
            "watchlist_listings": my_watchlist_listings,
            "amount_of_bids": amount_of_bids,
            "current_bid": current_bid,
            "comments": Comments.objects.filter(listing=listing)
        })

    return render(request, "auctions/listings.html", {
        "listing": listing,
        "amount_of_bids": amount_of_bids,
        "current_bid": current_bid,
        "comments": Comments.objects.filter(listing=listing)
    })


def close(request, listing_id):
    listing = Auction.objects.get(id=listing_id)
    bids_for_listing = Bids.objects.filter(listing=listing)

    if bids_for_listing:
        other_bids_prices = bids_for_listing.values_list('bid_price', flat=True)
        highest_price = max(other_bids_prices)    
                
        listing.winner = bids_for_listing.get(bid_price=highest_price).username 
        listing.active = False
        listing.save()
    else:
        listing.winner = listing.username
        listing.active = False
        listing.save()

    return HttpResponseRedirect(reverse("listings", args=[listing_id]))            


def watch(request, listing_id):
    listing = Auction.objects.get(id=listing_id)    
    Watchlist.objects.create(username=request.user.username, listing=listing)
    return HttpResponseRedirect(reverse("watchlist"))


def unwatch(request, listing_id):
    listing = Auction.objects.get(id=listing_id)
    this_listing = Watchlist.objects.get(username=request.user.username, listing=listing)
    this_listing.delete()
    return HttpResponseRedirect(reverse("watchlist"))


def watchlist(request):
    watchlist = Watchlist.objects.filter(username=request.user.username)
    mapped_watchlist = [watchlist_object.listing for watchlist_object in watchlist]

    return render(request, "auctions/watchlist.html", {
        "listings": mapped_watchlist
    })


def categories(request):
    categories = Auction.objects.values_list('category', flat=True).distinct()
    
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category):
    active_listings_in_category = Auction.objects.filter(category=category, 
                                                         active=True)    

    return render(request, "auctions/category.html", {
        "active_listings_in_category": active_listings_in_category,
        "category": category
    })  