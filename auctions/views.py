from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Categories, Listings, Bids, Comments


def index(request):
    user = request.user
    listings_count = []

    try:
        listings_count = user.user_watchlist.all()
    except AttributeError:
        pass
    return render(request, 'auctions/index.html', {
        'listings': Listings.objects.filter(is_active=True),
        'watchlist_count': len(listings_count)
    })

def login_view(request):
    if request.method == 'POST':

        # Attempt to sign user in
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'auctions/login.html', {
                'message': 'Invalid username and/or password.'
            })
    else:
        return render(request, 'auctions/login.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        # Ensure password matches confirmation
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'auctions/register.html', {
                'message': 'Passwords must match.'
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, 'auctions/register.html', {
                'message': 'Username already taken.'
            })
        login(request, user)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'auctions/register.html')

@login_required
def create_listing(request):
    if request.method == 'GET':
        user = request.user
        listings = user.user_watchlist.all()
        return render(request, 'auctions/create_listing.html', {
            'categories': Categories.objects.all(),
            'watchlist_count': len(listings)
        })

    if request.method == 'POST':
        title = request.POST['title']
        bid = request.POST['bid']
        img = request.POST['img']
        description = request.POST['description']
        category = request.POST['category']

        user = request.user
        category_content = Categories.objects.get(category=category)

        new_listing = Listings(title=title, starting_bid=float(bid), image=img, description=description, category=category_content, owner=user)
        new_listing.save()

        return HttpResponseRedirect(reverse('index'))

def categories_view(request):
    user = request.user 
    listings = user.user_watchlist.all()
    return render(request, 'auctions/categories.html', {
        'categories': Categories.objects.all(),
        'watchlist_count': len(listings)
    })

def category(request, category_name):
    category_type = Categories.objects.get(category=category_name)
    user = request.user 
    listings = user.user_watchlist.all()
    
    return render(request, 'auctions/category.html', {
        'category': Listings.objects.filter(is_active=True, category=category_type),
        'name_of_category': category_type,
        'watchlist_count': len(listings)
    })

def listing_view(request, id):
    listing = Listings.objects.get(pk=id)
    is_listing_in_watchlist = False
    user = request.user
    watchlist_count = []
    bids = listing.bid_listing.all()
    greater_bid = listing.starting_bid

    try:
        watchlist_count = user.user_watchlist.all()
    except AttributeError:
        pass
    
    if len(bids) > 0:
        for bid in bids:
            if bid.bid > greater_bid:
                greater_bid = bid.bid

    if user in listing.watchlist.all():
        is_listing_in_watchlist = True

    return render(request, 'auctions/listing_view.html', {
        'listing': listing,
        'is_listing_in_watchlist': is_listing_in_watchlist,
        'comments': Comments.objects.filter(listing=listing),
        'watchlist_count': len(watchlist_count),
        'item_bids': len(bids),
        'greater_bid': greater_bid,
        'msg': 'This listing is no longer active.',
        'winner_msg': 'YOU ARE THE WINNER!'
    })

@login_required
def handle_watchlist(request, id):
    listing = Listings.objects.get(pk=id)
    user = request.user

    if user in listing.watchlist.all():
        listing.watchlist.remove(user)
    else:
        listing.watchlist.add(user)

    return HttpResponseRedirect(reverse('listing', args=(id, )))

@login_required
def handle_bid(request, id):
    bid = request.POST['bid']
    user = request.user
    listing = Listings.objects.get(pk=id)
    item_bids = listing.bid_listing.all()

    try:
        greater_bid = float(bid)
        if greater_bid > listing.starting_bid:
            if len(item_bids) > 0:
                for b in item_bids:
                    if greater_bid <= b.bid:
                        messages.add_message(request, messages.ERROR, 'The bid must be greater than any other bids that have been placed.')
                        return HttpResponseRedirect(reverse('listing', args=(id,)))
            
            new_bid = Bids(bid=greater_bid, bidder=user, listing=listing)
            new_bid.save()
            messages.add_message(request, messages.SUCCESS,'Your bid was successfully placed.')


        else:
            messages.add_message(request, messages.ERROR, 'The bid must be at least as large as the starting bid.')

    except ValueError:
        messages.add_message(request, messages.ERROR, 'The bid must be at least as large as the starting bid.')

    return HttpResponseRedirect(reverse('listing', args=(id,)))

@login_required
def watchlist_view(request):
    user = request.user
    listings = user.user_watchlist.all()
    

    return render(request, 'auctions/watchlist.html', {
        'listings': listings,
        'watchlist_count': len(listings)
    })

@login_required
def comment(request, id):
    msg = request.POST['comment']
    user = request.user
    listing = Listings.objects.get(pk=id)

    new_msg = Comments(comment=msg, author=user, listing=listing)
    new_msg.save()

    return HttpResponseRedirect(reverse('listing', args=(id, )))

@login_required
def close_auction(request, id):
    listing = Listings.objects.get(pk=id)
    listing_bids = listing.bid_listing.all()
    greater_bid = listing.starting_bid
    winner = ''

    if len(listing_bids) > 0:
        for bid in listing_bids:
            if bid.bid > greater_bid:
                greater_bid = bid.bid
                winner = bid.bidder
        listing.winner = winner
        
    listing.is_active = False
    listing.save()

    return HttpResponseRedirect(reverse('listing', args=(id, )))