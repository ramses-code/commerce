from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('create', views.create_listing, name='create'),
    path('categories', views.categories_view, name='categories'),
    path('categories/<str:category_name>', views.category, name='category'),
    path('listing/<int:id>', views.listing_view, name='listing'),
    path('watchlist/<int:id>', views.handle_watchlist, name='handle_watchlist'),
    path('bid/<int:id>', views.handle_bid, name='bid'),
    path('watchlist', views.watchlist_view, name='watchlist'),
    path('comment/<int:id>', views.comment, name='comment'),
    path('close/<int:id>', views.close_auction, name='close')
]
