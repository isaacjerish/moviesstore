from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from regions.models import State, MoviePopularity
from django.contrib.auth.models import User

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)

    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())

    if (movie_ids == []):
        return redirect('cart.index')
    
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)

    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()

    # Get user's state (default to Georgia for demo purposes)
    # In a real app, you'd get this from user profile or IP geolocation
    user_state = get_user_state(request.user)

    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
        
        # Update movie popularity for the user's state
        update_movie_popularity(movie, user_state, int(cart[str(movie.id)]))

    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html', {'template_data': template_data})


def get_user_state(user):
    """Get the user's state from their profile"""
    try:
        from accounts.models import UserProfile
        profile = UserProfile.objects.get(user=user)
        return profile.state
    except:
        # Fallback to Georgia if no profile exists
        try:
            return State.objects.get(name='Georgia')
        except State.DoesNotExist:
            return State.objects.first()


def update_movie_popularity(movie, state, quantity):
    """Update movie popularity data when a purchase is made"""
    if not state:
        return
        
    # Get or create MoviePopularity record for this movie and state
    movie_popularity, created = MoviePopularity.objects.get_or_create(
        movie=movie,
        state=state,
        defaults={'purchase_count': 0, 'view_count': 0}
    )
    
    # Update purchase count
    movie_popularity.purchase_count += quantity
    movie_popularity.save()