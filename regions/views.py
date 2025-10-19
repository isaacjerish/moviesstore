from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import State, MoviePopularity
from movies.models import Movie


def map_view(request):
    """Display the interactive US map with movie popularity data"""
    template_data = {
        "title": "Local Popularity Map",
    }
    return render(request, "regions/map.html", {"template_data": template_data})


@require_http_methods(["GET"])
def state_movies_api(request, state_id):
    """API endpoint to get trending movies for a specific state"""
    try:
        state = State.objects.get(id=state_id)
        # Get top 10 movies by total activity for this state
        popular_movies = MoviePopularity.objects.filter(state=state).order_by('-purchase_count', '-view_count')[:10]
        
        movies_data = []
        for movie_pop in popular_movies:
            movies_data.append({
                'id': movie_pop.movie.id,
                'name': movie_pop.movie.name,
                'purchase_count': movie_pop.purchase_count,
                'view_count': movie_pop.view_count,
                'total_activity': movie_pop.total_activity,
                'image_url': f'/media/movie_images/{movie_pop.movie.image}' if movie_pop.movie.image else None,
                'price': movie_pop.movie.price,
                'genre': movie_pop.movie.genre,
                'rating': movie_pop.movie.rating,
            })
        
        return JsonResponse({
            'state': {
                'id': state.id,
                'name': state.name,
                'abbreviation': state.abbreviation,
            },
            'movies': movies_data
        })
        
    except State.DoesNotExist:
        return JsonResponse({'error': 'State not found'}, status=404)


@require_http_methods(["GET"])
def global_trending_api(request):
    """API endpoint to get globally trending movies across all states"""
    # Get movies with highest total activity across all states
    movies_data = []
    
    # Aggregate popularity data by movie
    from django.db.models import Sum, Count
    movie_stats = MoviePopularity.objects.values('movie').annotate(
        total_purchases=Sum('purchase_count'),
        total_views=Sum('view_count'),
        state_count=Count('state')
    ).order_by('-total_purchases', '-total_views')[:20]
    
    for stat in movie_stats:
        movie = Movie.objects.get(id=stat['movie'])
        movies_data.append({
            'id': movie.id,
            'name': movie.name,
            'total_purchases': stat['total_purchases'],
            'total_views': stat['total_views'],
            'state_count': stat['state_count'],
            'image_url': f'/media/movie_images/{movie.image}' if movie.image else None,
            'price': movie.price,
            'genre': movie.genre,
            'rating': movie.rating,
        })
    
    return JsonResponse({'movies': movies_data})


@require_http_methods(["GET"])
def states_list_api(request):
    """API endpoint to get all states with their coordinates"""
    states = State.objects.all().order_by('name')
    states_data = []
    
    for state in states:
        states_data.append({
            'id': state.id,
            'name': state.name,
            'abbreviation': state.abbreviation,
            'center_lat': state.center_lat,
            'center_lng': state.center_lng,
        })
    
    return JsonResponse({'states': states_data})


@require_http_methods(["GET"])
def compare_states_api(request):
    """API endpoint to compare trending movies between two states"""
    state1_id = request.GET.get('state1')
    state2_id = request.GET.get('state2')
    
    if not state1_id or not state2_id:
        return JsonResponse({'error': 'Both state1 and state2 parameters are required'}, status=400)
    
    try:
        state1 = State.objects.get(id=state1_id)
        state2 = State.objects.get(id=state2_id)
        
        # Get top movies for each state
        state1_movies = MoviePopularity.objects.filter(state=state1).order_by('-purchase_count', '-view_count')[:10]
        state2_movies = MoviePopularity.objects.filter(state=state2).order_by('-purchase_count', '-view_count')[:10]
        
        # Convert to dictionaries for easier comparison
        state1_data = []
        for movie_pop in state1_movies:
            state1_data.append({
                'id': movie_pop.movie.id,
                'name': movie_pop.movie.name,
                'purchase_count': movie_pop.purchase_count,
                'view_count': movie_pop.view_count,
                'total_activity': movie_pop.total_activity,
                'image_url': f'/media/movie_images/{movie_pop.movie.image}' if movie_pop.movie.image else None,
                'price': movie_pop.movie.price,
                'genre': movie_pop.movie.genre,
                'rating': movie_pop.movie.rating,
            })
        
        state2_data = []
        for movie_pop in state2_movies:
            state2_data.append({
                'id': movie_pop.movie.id,
                'name': movie_pop.movie.name,
                'purchase_count': movie_pop.purchase_count,
                'view_count': movie_pop.view_count,
                'total_activity': movie_pop.total_activity,
                'image_url': f'/media/movie_images/{movie_pop.movie.image}' if movie_pop.movie.image else None,
                'price': movie_pop.movie.price,
                'genre': movie_pop.movie.genre,
                'rating': movie_pop.movie.rating,
            })
        
        return JsonResponse({
            'state1': {
                'id': state1.id,
                'name': state1.name,
                'abbreviation': state1.abbreviation,
                'movies': state1_data
            },
            'state2': {
                'id': state2.id,
                'name': state2.name,
                'abbreviation': state2.abbreviation,
                'movies': state2_data
            }
        })
        
    except State.DoesNotExist:
        return JsonResponse({'error': 'One or both states not found'}, status=404)


@require_http_methods(["GET"])
def personal_purchases_api(request):
    """API endpoint to get user's personal purchase history"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get user's recent purchases
    from cart.models import Order, Item
    from django.db.models import Sum
    
    # Get user's orders with movie details
    orders = Order.objects.filter(user=request.user).order_by('-date')[:10]
    
    # Aggregate purchases by movie
    movie_purchases = {}
    for order in orders:
        items = Item.objects.filter(order=order)
        for item in items:
            movie_id = item.movie.id
            if movie_id not in movie_purchases:
                movie_purchases[movie_id] = {
                    'movie': item.movie,
                    'total_quantity': 0,
                    'total_spent': 0,
                    'purchase_dates': []
                }
            movie_purchases[movie_id]['total_quantity'] += item.quantity
            movie_purchases[movie_id]['total_spent'] += item.price * item.quantity
            movie_purchases[movie_id]['purchase_dates'].append(order.date.strftime('%Y-%m-%d'))
    
    # Convert to list and sort by total quantity
    personal_data = []
    for movie_id, data in movie_purchases.items():
        personal_data.append({
            'id': data['movie'].id,
            'name': data['movie'].name,
            'total_quantity': data['total_quantity'],
            'total_spent': data['total_spent'],
            'purchase_dates': data['purchase_dates'],
            'image_url': f'/media/movie_images/{data["movie"].image}' if data['movie'].image else None,
            'price': data['movie'].price,
            'genre': data['movie'].genre,
            'rating': data['movie'].rating,
        })
    
    # Sort by total quantity (most purchased first)
    personal_data.sort(key=lambda x: x['total_quantity'], reverse=True)
    
    return JsonResponse({
        'user': {
            'username': request.user.username,
            'purchases': personal_data[:10]  # Top 10 personal purchases
        }
    })


@require_http_methods(["GET"])
def other_users_api(request):
    """API endpoint to get other users' purchase data from a specific state"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    from cart.models import Order, Item
    from django.contrib.auth.models import User
    from django.db.models import Sum, Count
    from accounts.models import UserProfile
    
    # Get state parameter
    state_id = request.GET.get('state_id')
    
    if state_id:
        try:
            target_state = State.objects.get(id=state_id)
            # Get users from the specific state (excluding current user)
            other_users = User.objects.filter(
                userprofile__state=target_state
            ).exclude(id=request.user.id)
            state_name = target_state.name
        except State.DoesNotExist:
            return JsonResponse({'error': 'State not found'}, status=404)
    else:
        # If no state specified, get all users except current user
        other_users = User.objects.exclude(id=request.user.id)
        state_name = "All States"
    
    # Get purchase data for other users
    users_data = []
    for user in other_users[:15]:  # Limit to 15 other users
        # Get user's recent purchases
        orders = Order.objects.filter(user=user).order_by('-date')[:5]
        
        # Aggregate purchases by movie
        movie_purchases = {}
        for order in orders:
            items = Item.objects.filter(order=order)
            for item in items:
                movie_id = item.movie.id
                if movie_id not in movie_purchases:
                    movie_purchases[movie_id] = {
                        'movie': item.movie,
                        'total_quantity': 0,
                        'total_spent': 0
                    }
                movie_purchases[movie_id]['total_quantity'] += item.quantity
                movie_purchases[movie_id]['total_spent'] += item.price * item.quantity
        
        # Convert to list and sort by total quantity
        user_purchases = []
        for movie_id, data in movie_purchases.items():
            user_purchases.append({
                'id': data['movie'].id,
                'name': data['movie'].name,
                'total_quantity': data['total_quantity'],
                'total_spent': data['total_spent'],
                'image_url': f'/media/movie_images/{data["movie"].image}' if data['movie'].image else None,
                'price': data['movie'].price,
                'genre': data['movie'].genre,
                'rating': data['movie'].rating,
            })
        
        # Sort by total quantity
        user_purchases.sort(key=lambda x: x['total_quantity'], reverse=True)
        
        if user_purchases:  # Only include users with purchases
            users_data.append({
                'username': user.username,
                'purchases': user_purchases[:5]  # Top 5 purchases per user
            })
    
    return JsonResponse({
        'users': users_data,
        'state_name': state_name,
        'total_users': len(users_data)
    })


@require_http_methods(["GET"])
def compare_personal_state_api(request):
    """API endpoint to compare user's personal purchases with their state's trending"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get user's state
    try:
        from accounts.models import UserProfile
        profile = UserProfile.objects.get(user=request.user)
        user_state = profile.state
    except:
        try:
            user_state = State.objects.get(name='Georgia')
        except State.DoesNotExist:
            user_state = State.objects.first()
    
    if not user_state:
        return JsonResponse({'error': 'User state not found'}, status=404)
    
    # Get user's personal purchases (reuse logic from personal_purchases_api)
    from cart.models import Order, Item
    
    orders = Order.objects.filter(user=request.user).order_by('-date')[:10]
    movie_purchases = {}
    for order in orders:
        items = Item.objects.filter(order=order)
        for item in items:
            movie_id = item.movie.id
            if movie_id not in movie_purchases:
                movie_purchases[movie_id] = {
                    'movie': item.movie,
                    'total_quantity': 0,
                    'total_spent': 0
                }
            movie_purchases[movie_id]['total_quantity'] += item.quantity
            movie_purchases[movie_id]['total_spent'] += item.price * item.quantity
    
    # Get state trending data
    state_movies = MoviePopularity.objects.filter(state=user_state).order_by('-purchase_count', '-view_count')[:10]
    
    # Convert personal data
    personal_data = []
    for movie_id, data in movie_purchases.items():
        personal_data.append({
            'id': data['movie'].id,
            'name': data['movie'].name,
            'total_quantity': data['total_quantity'],
            'total_spent': data['total_spent'],
            'image_url': f'/media/movie_images/{data["movie"].image}' if data['movie'].image else None,
            'price': data['movie'].price,
            'genre': data['movie'].genre,
            'rating': data['movie'].rating,
        })
    
    # Convert state data
    state_data = []
    for movie_pop in state_movies:
        state_data.append({
            'id': movie_pop.movie.id,
            'name': movie_pop.movie.name,
            'purchase_count': movie_pop.purchase_count,
            'view_count': movie_pop.view_count,
            'total_activity': movie_pop.total_activity,
            'image_url': f'/media/movie_images/{movie_pop.movie.image}' if movie_pop.movie.image else None,
            'price': movie_pop.movie.price,
            'genre': movie_pop.movie.genre,
            'rating': movie_pop.movie.rating,
        })
    
    return JsonResponse({
        'personal': {
            'username': request.user.username,
            'movies': personal_data
        },
        'state': {
            'name': user_state.name,
            'movies': state_data
        }
    })