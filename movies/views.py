from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from regions.models import State, MoviePopularity
import json


def index(request):
    search_term = request.GET.get("search")
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data["title"] = "Movies"
    template_data["movies"] = movies
    return render(request, "movies/index.html", {"template_data": template_data})


def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, is_reported=False)
    
    # Track movie view for popularity
    track_movie_view(movie, request.user)
    
    template_data = {}
    template_data["title"] = movie.name
    template_data["movie"] = movie
    template_data["reviews"] = reviews
    return render(request, "movies/show.html", {"template_data": template_data})


@login_required
def create_review(request, id):
    if request.method == "POST" and request.POST["comment"] != "":
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST["comment"]
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect("movies.show", id=id)
    else:
        return redirect("movies.show", id=id)


@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect("movies.show", id=id)

    if request.method == "GET":
        template_data = {}
        template_data["title"] = "Edit Review"
        template_data["review"] = review
        return render(
            request, "movies/edit_review.html", {"template_data": template_data}
        )
    elif request.method == "POST" and request.POST["comment"] != "":
        review = Review.objects.get(id=review_id)
        review.comment = request.POST["comment"]
        review.save()
        return redirect("movies.show", id=id)
    else:
        return redirect("movies.show", id=id)


@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect("movies.show", id=id)


@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_reported = True
    review.save()
    return redirect("movies.show", id=id)


@login_required
@require_POST
@csrf_exempt
def submit_rating(request, id):
    try:
        movie = get_object_or_404(Movie, id=id)
        data = json.loads(request.body)
        rating_value = int(data.get('rating'))
        
        # Validate rating value
        if rating_value < 1 or rating_value > 5:
            return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        
        # Get or create rating (update if exists due to unique_together constraint)
        rating, created = Rating.objects.get_or_create(
            user=request.user,
            movie=movie,
            defaults={'rating': rating_value}
        )
        
        if not created:
            # Update existing rating
            rating.rating = rating_value
            rating.save()
        
        return JsonResponse({
            'success': True,
            'rating': rating_value,
            'message': 'Rating submitted successfully'
        })
        
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid rating data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)


def rating_summary(request, id):
    try:
        movie = get_object_or_404(Movie, id=id)
        ratings = movie.user_ratings.all()
        
        if not ratings.exists():
            return JsonResponse({
                'average_rating': 0,
                'total_ratings': 0,
                'rating_distribution': {str(i): 0 for i in range(1, 6)}
            })
        
        # Calculate average rating
        total_ratings = ratings.count()
        average_rating = sum(r.rating for r in ratings) / total_ratings
        
        # Calculate rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            count = ratings.filter(rating=i).count()
            rating_distribution[str(i)] = count
        
        return JsonResponse({
            'average_rating': round(average_rating, 2),
            'total_ratings': total_ratings,
            'rating_distribution': rating_distribution
        })
        
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)


def track_movie_view(movie, user):
    """Track movie view for popularity calculation"""
    if not user.is_authenticated:
        return
        
    # Get user's state from their profile
    try:
        from accounts.models import UserProfile
        profile = UserProfile.objects.get(user=user)
        user_state = profile.state
    except:
        # Fallback to Georgia if no profile exists
        try:
            user_state = State.objects.get(name='Georgia')
        except State.DoesNotExist:
            user_state = State.objects.first()
    
    if not user_state:
        return
    
    # Get or create MoviePopularity record for this movie and state
    movie_popularity, created = MoviePopularity.objects.get_or_create(
        movie=movie,
        state=user_state,
        defaults={'purchase_count': 0, 'view_count': 0}
    )
    
    # Update view count
    movie_popularity.view_count += 1
    movie_popularity.save()
