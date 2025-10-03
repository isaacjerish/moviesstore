from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Petition, Vote
from movies.models import Movie


class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ['user', 'created_at']
    can_delete = False


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'movie_title', 'created_by', 'votes_count', 'status', 'created_at', 'is_expired_display']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'movie_title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'votes_count']
    inlines = [VoteInline]
    
    fieldsets = (
        ('Petition Details', {
            'fields': ('title', 'description', 'created_by', 'created_at')
        }),
        ('Movie Information', {
            'fields': ('movie_title', 'movie_year', 'movie_director', 'movie_genre')
        }),
        ('Status & Votes', {
            'fields': ('status', 'votes_count')
        }),
    )
    
    actions = ['approve_petitions', 'reject_petitions']
    
    def is_expired_display(self, obj):
        """Display if petition is expired"""
        return obj.is_expired
    is_expired_display.boolean = True
    is_expired_display.short_description = 'Expired'
    
    def approve_petitions(self, request, queryset):
        """Approve selected petitions and create movies"""
        approved_count = 0
        for petition in queryset.filter(status='pending'):
            # Create movie from petition
            movie = Movie(
                name=petition.movie_title,
                price=15,  # Default price
                description=petition.description,
                image='movie_images/default.jpg',  # Default image
                release_year=petition.movie_year or 2000,
                director=petition.movie_director or 'Unknown',
                genre=petition.movie_genre or 'Action',
                rating='PG'  # Default rating
            )
            movie.save()
            
            # Update petition status
            petition.status = 'approved'
            petition.save()
            approved_count += 1
        
        self.message_user(request, f'{approved_count} petitions approved and movies created.')
    approve_petitions.short_description = 'Approve selected petitions and create movies'
    
    def reject_petitions(self, request, queryset):
        """Reject selected petitions"""
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{updated} petitions rejected.')
    reject_petitions.short_description = 'Reject selected petitions'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'petition', 'created_at']
    list_filter = ['created_at', 'petition__status']
    search_fields = ['user__username', 'petition__title']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'petition')