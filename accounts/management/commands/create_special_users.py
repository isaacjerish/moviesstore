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
    help = 'Create special users with specific purchase patterns'

    def handle(self, *args, **options):
        self.stdout.write('Creating special users with specific patterns...')
        
        # Create users with specific movie preferences
        self.create_movie_fanatics()
        self.create_state_specific_users()
        self.create_recent_buyers()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created special users!')
        )

    def create_movie_fanatics(self):
        """Create users who buy lots of movies"""
        states = list(State.objects.all())
        movies = list(Movie.objects.all())
        
        for i in range(10):  # 10 movie fanatics
            username = f'moviefan{i+1}'
            if User.objects.filter(username=username).exists():
                continue
                
            user = User.objects.create_user(
                username=username,
                email=f'moviefan{i+1}@example.com',
                password='testpass123',
                first_name=f'MovieFan{i+1}',
                last_name='Enthusiast'
            )
            
            # Assign to random state
            state = random.choice(states)
            UserProfile.objects.create(user=user, state=state)
            
            # Create many purchases
            for purchase_num in range(random.randint(8, 15)):  # 8-15 orders
                order = Order.objects.create(
                    user=user,
                    total=0,
                    date=timezone.now() - timedelta(days=random.randint(0, 60))
                )
                
                # Buy multiple movies per order
                num_items = random.randint(2, 4)
                selected_movies = random.sample(movies, min(num_items, len(movies)))
                
                order_total = 0
                for movie in selected_movies:
                    quantity = random.randint(1, 3)
                    Item.objects.create(
                        order=order,
                        movie=movie,
                        price=movie.price,
                        quantity=quantity
                    )
                    order_total += movie.price * quantity
                    
                    # Update popularity
                    self.update_movie_popularity(movie, state, quantity)
                
                order.total = order_total
                order.save()

    def create_state_specific_users(self):
        """Create users in specific states with specific movie preferences"""
        # California users love action movies
        california = State.objects.get(name='California')
        action_movies = Movie.objects.filter(genre='Action')
        
        for i in range(5):
            username = f'californian{i+1}'
            if User.objects.filter(username=username).exists():
                continue
                
            user = User.objects.create_user(
                username=username,
                email=f'californian{i+1}@example.com',
                password='testpass123',
                first_name=f'Californian{i+1}',
                last_name='ActionLover'
            )
            
            UserProfile.objects.create(user=user, state=california)
            
            # Buy mostly action movies
            for purchase_num in range(random.randint(3, 6)):
                order = Order.objects.create(
                    user=user,
                    total=0,
                    date=timezone.now() - timedelta(days=random.randint(0, 45))
                )
                
                # Prefer action movies
                if action_movies.exists() and random.random() < 0.7:
                    movie = random.choice(action_movies)
                else:
                    movie = random.choice(Movie.objects.all())
                
                quantity = random.randint(1, 2)
                Item.objects.create(
                    order=order,
                    movie=movie,
                    price=movie.price,
                    quantity=quantity
                )
                order.total = movie.price * quantity
                order.save()
                
                self.update_movie_popularity(movie, california, quantity)
        
        # New York users love sci-fi
        new_york = State.objects.get(name='New York')
        scifi_movies = Movie.objects.filter(genre='Sci-Fi')
        
        for i in range(5):
            username = f'newyorker{i+1}'
            if User.objects.filter(username=username).exists():
                continue
                
            user = User.objects.create_user(
                username=username,
                email=f'newyorker{i+1}@example.com',
                password='testpass123',
                first_name=f'NewYorker{i+1}',
                last_name='SciFiFan'
            )
            
            UserProfile.objects.create(user=user, state=new_york)
            
            # Buy mostly sci-fi movies
            for purchase_num in range(random.randint(3, 6)):
                order = Order.objects.create(
                    user=user,
                    total=0,
                    date=timezone.now() - timedelta(days=random.randint(0, 45))
                )
                
                # Prefer sci-fi movies
                if scifi_movies.exists() and random.random() < 0.7:
                    movie = random.choice(scifi_movies)
                else:
                    movie = random.choice(Movie.objects.all())
                
                quantity = random.randint(1, 2)
                Item.objects.create(
                    order=order,
                    movie=movie,
                    price=movie.price,
                    quantity=quantity
                )
                order.total = movie.price * quantity
                order.save()
                
                self.update_movie_popularity(movie, new_york, quantity)

    def create_recent_buyers(self):
        """Create users who made recent purchases"""
        states = list(State.objects.all())
        movies = list(Movie.objects.all())
        
        for i in range(15):  # 15 recent buyers
            username = f'recentbuyer{i+1}'
            if User.objects.filter(username=username).exists():
                continue
                
            user = User.objects.create_user(
                username=username,
                email=f'recentbuyer{i+1}@example.com',
                password='testpass123',
                first_name=f'Recent{i+1}',
                last_name='Buyer'
            )
            
            state = random.choice(states)
            UserProfile.objects.create(user=user, state=state)
            
            # Create recent purchases (last 7 days)
            for purchase_num in range(random.randint(1, 3)):
                order = Order.objects.create(
                    user=user,
                    total=0,
                    date=timezone.now() - timedelta(days=random.randint(0, 7))
                )
                
                num_items = random.randint(1, 2)
                selected_movies = random.sample(movies, min(num_items, len(movies)))
                
                order_total = 0
                for movie in selected_movies:
                    quantity = random.randint(1, 2)
                    Item.objects.create(
                        order=order,
                        movie=movie,
                        price=movie.price,
                        quantity=quantity
                    )
                    order_total += movie.price * quantity
                    
                    self.update_movie_popularity(movie, state, quantity)
                
                order.total = order_total
                order.save()

    def update_movie_popularity(self, movie, state, quantity):
        """Update movie popularity data based on real purchase"""
        movie_popularity, created = MoviePopularity.objects.get_or_create(
            movie=movie,
            state=state,
            defaults={'purchase_count': 0, 'view_count': 0}
        )
        
        movie_popularity.purchase_count += quantity
        
        # Add some views
        views_to_add = random.randint(0, 2)
        movie_popularity.view_count += views_to_add
        
        movie_popularity.save()
