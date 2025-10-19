from django.core.management.base import BaseCommand
from django.utils import timezone
from regions.models import State, MoviePopularity
from movies.models import Movie
import random


class Command(BaseCommand):
    help = 'Populate US states and mock movie popularity data'

    def handle(self, *args, **options):
        self.stdout.write('Creating US states...')
        self.create_states()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated regions data!')
        )
        self.stdout.write(
            self.style.WARNING('Note: Run create_users_with_purchases to generate real user data.')
        )

    def create_states(self):
        """Create US states with coordinates"""
        states_data = [
            ('Alabama', 'AL', 32.806671, -86.791130),
            ('Alaska', 'AK', 61.370716, -152.404419),
            ('Arizona', 'AZ', 33.729759, -111.431221),
            ('Arkansas', 'AR', 34.969704, -92.373123),
            ('California', 'CA', 36.116203, -119.681564),
            ('Colorado', 'CO', 39.059811, -105.311104),
            ('Connecticut', 'CT', 41.597782, -72.755371),
            ('Delaware', 'DE', 39.318523, -75.507141),
            ('Florida', 'FL', 27.766279, -81.686783),
            ('Georgia', 'GA', 33.040619, -83.643074),
            ('Hawaii', 'HI', 21.094318, -157.498337),
            ('Idaho', 'ID', 44.240459, -114.478828),
            ('Illinois', 'IL', 40.349457, -88.986137),
            ('Indiana', 'IN', 39.849426, -86.258278),
            ('Iowa', 'IA', 42.011539, -93.210526),
            ('Kansas', 'KS', 38.526600, -96.726486),
            ('Kentucky', 'KY', 37.668140, -84.670067),
            ('Louisiana', 'LA', 31.169546, -91.867805),
            ('Maine', 'ME', 44.323535, -69.765261),
            ('Maryland', 'MD', 39.063946, -76.802101),
            ('Massachusetts', 'MA', 42.230171, -71.530106),
            ('Michigan', 'MI', 43.326618, -84.536095),
            ('Minnesota', 'MN', 45.694454, -93.900192),
            ('Mississippi', 'MS', 32.741646, -89.678696),
            ('Missouri', 'MO', 38.456085, -92.288368),
            ('Montana', 'MT', 47.052632, -110.454353),
            ('Nebraska', 'NE', 41.125370, -98.268082),
            ('Nevada', 'NV', 38.313515, -117.055374),
            ('New Hampshire', 'NH', 43.452492, -71.563896),
            ('New Jersey', 'NJ', 40.298904, -74.521011),
            ('New Mexico', 'NM', 34.840515, -106.248482),
            ('New York', 'NY', 42.165726, -74.948051),
            ('North Carolina', 'NC', 35.630066, -79.806419),
            ('North Dakota', 'ND', 47.528912, -99.784012),
            ('Ohio', 'OH', 40.388783, -82.764915),
            ('Oklahoma', 'OK', 35.565342, -96.928917),
            ('Oregon', 'OR', 44.572021, -122.070938),
            ('Pennsylvania', 'PA', 40.590752, -77.209755),
            ('Rhode Island', 'RI', 41.680893, -71.51178),
            ('South Carolina', 'SC', 33.856892, -80.945007),
            ('South Dakota', 'SD', 44.299782, -99.438828),
            ('Tennessee', 'TN', 35.747845, -86.692345),
            ('Texas', 'TX', 31.054487, -97.563461),
            ('Utah', 'UT', 40.150032, -111.862434),
            ('Vermont', 'VT', 44.045876, -72.710686),
            ('Virginia', 'VA', 37.769337, -78.169968),
            ('Washington', 'WA', 47.400902, -121.490494),
            ('West Virginia', 'WV', 38.491226, -80.954453),
            ('Wisconsin', 'WI', 44.268543, -89.616508),
            ('Wyoming', 'WY', 42.755966, -107.302490),
        ]
        
        for name, abbr, lat, lng in states_data:
            State.objects.get_or_create(
                name=name,
                defaults={
                    'abbreviation': abbr,
                    'center_lat': lat,
                    'center_lng': lng
                }
            )

