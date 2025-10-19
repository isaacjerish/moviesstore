from django.core.management.base import BaseCommand
from movies.models import Movie


class Command(BaseCommand):
    help = 'Populate sample movies for the movie store'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample movies...')
        self.create_sample_movies()
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample movies!')
        )

    def create_sample_movies(self):
        """Create sample movies"""
        movies_data = [
            {
                'name': 'Inception',
                'price': 15,
                'description': 'A mind-bending thriller about dreams within dreams.',
                'image': 'inception.jpg',
                'release_year': 2010,
                'director': 'Christopher Nolan',
                'genre': 'Sci-Fi',
                'rating': 'PG-13'
            },
            {
                'name': 'The Dark Knight',
                'price': 18,
                'description': 'Batman faces the Joker in this epic superhero film.',
                'image': 'dark.jpg',
                'release_year': 2008,
                'director': 'Christopher Nolan',
                'genre': 'Action',
                'rating': 'PG-13'
            },
            {
                'name': 'Avatar',
                'price': 20,
                'description': 'A sci-fi epic about the planet Pandora.',
                'image': 'avatar.jpg',
                'release_year': 2009,
                'director': 'James Cameron',
                'genre': 'Sci-Fi',
                'rating': 'PG-13'
            },
            {
                'name': 'Titanic',
                'price': 12,
                'description': 'A romantic drama set on the ill-fated ship.',
                'image': 'titanic.jpg',
                'release_year': 1997,
                'director': 'James Cameron',
                'genre': 'Romance',
                'rating': 'PG-13'
            },
            {
                'name': 'Real Steel',
                'price': 14,
                'description': 'A father and son bond through robot boxing.',
                'image': 'real.jpeg',
                'release_year': 2011,
                'director': 'Shawn Levy',
                'genre': 'Action',
                'rating': 'PG-13'
            }
        ]
        
        for movie_data in movies_data:
            Movie.objects.get_or_create(
                name=movie_data['name'],
                defaults=movie_data
            )
        
        self.stdout.write(f'Created {len(movies_data)} sample movies')
