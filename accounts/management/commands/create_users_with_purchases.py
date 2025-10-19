from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile
from regions.models import State, MoviePopularity
from movies.models import Movie
from cart.models import Order, Item
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Create real users with actual purchases in different states'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        
        self.stdout.write('Creating real users with purchases...')
        
        # Clear existing mock data
        self.clear_mock_data()
        
        # Create users with purchases
        self.create_users_with_purchases(num_users)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {num_users} users with real purchases!')
        )

    def clear_mock_data(self):
        """Clear existing mock popularity data"""
        self.stdout.write('Clearing existing mock data...')
        MoviePopularity.objects.all().delete()
        
        # Clear existing test users (optional - be careful in production)
        test_users = User.objects.filter(username__startswith='testuser')
        for user in test_users:
            user.delete()

    def create_users_with_purchases(self, num_users):
        """Create real users with actual purchases"""
        states = list(State.objects.all())
        movies = list(Movie.objects.all())
        
        if not states:
            self.stdout.write(self.style.ERROR('No states found. Run populate_regions first.'))
            return
            
        if not movies:
            self.stdout.write(self.style.ERROR('No movies found. Run populate_movies first.'))
            return
        
        # State distribution - some states get more users
        state_weights = {
            'California': 0.15,
            'Texas': 0.12,
            'New York': 0.10,
            'Florida': 0.08,
            'Georgia': 0.05,
        }
        
        # Default weight for other states
        default_weight = 0.5 / (len(states) - len(state_weights))
        
        for i in range(num_users):
            # Create user
            username = f'testuser{i+1}'
            email = f'testuser{i+1}@example.com'
            
            # Skip if user already exists
            if User.objects.filter(username=username).exists():
                continue
                
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',
                first_name=f'Test{i+1}',
                last_name='User'
            )
            
            # Assign user to a state
            state = self.select_weighted_state(states, state_weights, default_weight)
            UserProfile.objects.create(user=user, state=state)
            
            # Create purchases for this user
            num_purchases = random.randint(1, 5)  # 1-5 purchase orders per user
            
            for purchase_num in range(num_purchases):
                # Create order
                order = Order.objects.create(
                    user=user,
                    total=0,  # Will be calculated
                    date=timezone.now() - timedelta(days=random.randint(0, 30))
                )
                
                # Add items to order
                num_items = random.randint(1, 3)  # 1-3 movies per order
                selected_movies = random.sample(movies, min(num_items, len(movies)))
                
                order_total = 0
                for movie in selected_movies:
                    quantity = random.randint(1, 2)  # 1-2 copies per movie
                    item = Item.objects.create(
                        order=order,
                        movie=movie,
                        price=movie.price,
                        quantity=quantity
                    )
                    order_total += movie.price * quantity
                    
                    # Update movie popularity for this state
                    self.update_movie_popularity(movie, state, quantity)
                
                # Update order total
                order.total = order_total
                order.save()
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'Created {i + 1} users...')

    def select_weighted_state(self, states, state_weights, default_weight):
        """Select a state based on weights"""
        weights = []
        for state in states:
            weight = state_weights.get(state.name, default_weight)
            weights.append(weight)
        
        return random.choices(states, weights=weights)[0]

    def update_movie_popularity(self, movie, state, quantity):
        """Update movie popularity data based on real purchase"""
        movie_popularity, created = MoviePopularity.objects.get_or_create(
            movie=movie,
            state=state,
            defaults={'purchase_count': 0, 'view_count': 0}
        )
        
        # Update purchase count
        movie_popularity.purchase_count += quantity
        
        # Add some random views (simulating people viewing movies)
        views_to_add = random.randint(0, 3)
        movie_popularity.view_count += views_to_add
        
        movie_popularity.save()
