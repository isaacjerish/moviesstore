# Generated manually to fix ImageField issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0008_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='image',
            field=models.CharField(default='dummy_movie.png', max_length=255),
        ),
    ]
