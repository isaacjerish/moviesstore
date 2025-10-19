from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from regions.models import State, MoviePopularity
from movies.models import Movie
from cart.models import Order, Item
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Show statistics about the real user data'

    def handle(self, *args, **options):
        self.stdout.write('=== REAL USER DATA STATISTICS ===\n')
        
        # User statistics
        total_users = User.objects.count()
        users_with_profiles = UserProfile.objects.count()
        users_with_purchases = User.objects.filter(order__isnull=False).distinct().count()
        
        self.stdout.write(f'Total Users: {total_users}')
        self.stdout.write(f'Users with State Profiles: {users_with_profiles}')
        self.stdout.write(f'Users with Purchases: {users_with_purchases}\n')
        
        # Purchase statistics
        total_orders = Order.objects.count()
        total_items = Item.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0
        
        self.stdout.write(f'Total Orders: {total_orders}')
        self.stdout.write(f'Total Items Sold: {total_items}')
        self.stdout.write(f'Total Revenue: ${total_revenue}\n')
        
        # State statistics
        self.stdout.write('=== STATE PURCHASE STATISTICS ===')
        state_stats = State.objects.annotate(
            user_count=Count('userprofile'),
            purchase_count=Sum('moviepopularity__purchase_count')
        ).order_by('-purchase_count')
        
        for state in state_stats[:10]:  # Top 10 states
            self.stdout.write(f'{state.name}: {state.user_count} users, {state.purchase_count or 0} purchases')
        
        # Movie popularity by state
        self.stdout.write('\n=== TOP TRENDING MOVIES BY STATE ===')
        for state in State.objects.all()[:5]:  # Show top 5 states
            self.stdout.write(f'\n{state.name}:')
            top_movies = MoviePopularity.objects.filter(state=state).order_by('-purchase_count')[:3]
            for movie_pop in top_movies:
                self.stdout.write(f'  - {movie_pop.movie.name}: {movie_pop.purchase_count} purchases, {movie_pop.view_count} views')
        
        # User purchase patterns
        self.stdout.write('\n=== USER PURCHASE PATTERNS ===')
        heavy_buyers = User.objects.annotate(
            order_count=Count('order')
        ).filter(order_count__gte=5).count()
        
        recent_buyers = User.objects.filter(
            order__date__gte=timezone.now() - timedelta(days=7)
        ).distinct().count()
        
        self.stdout.write(f'Heavy Buyers (5+ orders): {heavy_buyers}')
        self.stdout.write(f'Recent Buyers (last 7 days): {recent_buyers}')
        
        self.stdout.write('\n=== DATA IS NOW REAL! ===')
        self.stdout.write('All trending data is based on actual user purchases.')
