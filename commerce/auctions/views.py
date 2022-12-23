from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Categories, Listings, Bids, Comments


def index(request):
    return render(request, 'auctions/index.html', {
        'listings': Listings.objects.filter(is_active=True)
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
        return render(request, 'auctions/create_listing.html', {
            'categories': Categories.objects.all()
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
    return render(request, 'auctions/categories.html', {
        'categories': Categories.objects.all()
    })

def category(request, category_name):
    category_type = Categories.objects.get(category=category_name)
    
    return render(request, 'auctions/category.html', {
        'category': Listings.objects.filter(is_active=True, category=category_type),
        'name_of_category': category_type
    })

def listing_view(request, id):
    listing = Listings.objects.get(pk=id)
    is_listing_in_watchlist = False
    user = request.user

    if user in listing.watchlist.all():
        is_listing_in_watchlist = True

    return render(request, 'auctions/listing_view.html', {
        'listing': listing,
        'is_listing_in_watchlist': is_listing_in_watchlist,
        'comments': Comments.objects.filter(listing=listing)
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
    ...

@login_required
def watchlist_view(request):
    user = request.user
    listings = Listings.objects.filter(watchlist=user)
    

    return render(request, 'auctions/watchlist.html', {
        'listings': listings
    })

@login_required
def comment(request, id):
    msg = request.POST['comment']
    user = request.user
    listing = Listings.objects.get(pk=id)

    new_msg = Comments(comment=msg, author=user, listing=listing)
    new_msg.save()

    return HttpResponseRedirect(reverse('listing', args=(id, )))