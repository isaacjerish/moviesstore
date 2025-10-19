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