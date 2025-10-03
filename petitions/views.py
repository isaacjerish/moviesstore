from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError, models
from django.core.paginator import Paginator
from .models import Petition, Vote
from .forms import PetitionForm
from movies.models import Movie
from django.utils import timezone


def index(request):
    """Display all petitions with search and filtering"""
    search_term = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    
    petitions = Petition.objects.all()
    
    # Apply search filter
    if search_term:
        petitions = petitions.filter(
            models.Q(title__icontains=search_term) |
            models.Q(description__icontains=search_term) |
            models.Q(movie_title__icontains=search_term)
        )
    
    # Apply status filter
    if status_filter:
        petitions = petitions.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(petitions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    template_data = {
        "title": "Movie Petitions",
        "page_obj": page_obj,
        "search_term": search_term,
        "status_filter": status_filter,
        "status_choices": Petition.STATUS_CHOICES,
    }
    
    return render(request, "petitions/index.html", {"template_data": template_data})


@login_required
def create(request):
    """Create a new petition"""
    if request.method == "POST":
        form = PetitionForm(request.POST)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.created_by = request.user
            petition.save()
            messages.success(request, "Petition created successfully!")
            return redirect("petitions.show", id=petition.id)
    else:
        form = PetitionForm()
    
    template_data = {
        "title": "Create Petition",
        "form": form,
    }
    
    return render(request, "petitions/create.html", {"template_data": template_data})


def show(request, id):
    """Display petition details and voting interface"""
    petition = get_object_or_404(Petition, id=id)
    
    # Check if user has voted on this petition
    user_voted = False
    if request.user.is_authenticated:
        user_voted = Vote.objects.filter(petition=petition, user=request.user).exists()
    
    # Get recent votes for display
    recent_votes = Vote.objects.filter(petition=petition).select_related('user').order_by('-created_at')[:10]
    
    template_data = {
        "title": petition.title,
        "petition": petition,
        "user_voted": user_voted,
        "recent_votes": recent_votes,
    }
    
    return render(request, "petitions/show.html", {"template_data": template_data})


@login_required
def vote(request, id):
    """Handle voting on petitions"""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    petition = get_object_or_404(Petition, id=id)
    
    # Check if petition is still active
    if not petition.is_active:
        return JsonResponse({"error": "This petition is no longer active"}, status=400)
    
    # Check if user has already voted
    existing_vote = Vote.objects.filter(petition=petition, user=request.user).first()
    
    if existing_vote:
        # Remove vote (unvote)
        existing_vote.delete()
        petition.update_votes_count()
        return JsonResponse({
            "success": True,
            "action": "unvoted",
            "votes_count": petition.votes_count,
            "message": "Vote removed successfully"
        })
    else:
        # Add vote
        try:
            Vote.objects.create(petition=petition, user=request.user)
            petition.update_votes_count()
            return JsonResponse({
                "success": True,
                "action": "voted",
                "votes_count": petition.votes_count,
                "message": "Vote added successfully"
            })
        except IntegrityError:
            return JsonResponse({"error": "You have already voted on this petition"}, status=400)


@login_required
def my_petitions(request):
    """Display user's own petitions"""
    petitions = Petition.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(petitions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    template_data = {
        "title": "My Petitions",
        "page_obj": page_obj,
    }
    
    return render(request, "petitions/my_petitions.html", {"template_data": template_data})