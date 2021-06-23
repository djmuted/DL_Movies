import json

import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from movies.api.models import Movie
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Populates the movie database with movies_metadata.csv dataset'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='?', default='movies_metadata.csv')

    def handle(self, *args, **options):
        movie_count = Movie.objects.count()
        if movie_count > 1000:
            self.stdout.write(self.style.WARNING('Database is already populated with %d entries' % movie_count))
            return
        self.stdout.write('Reading %s' % options['csv_file'])
        df = pd.read_csv(options['csv_file'])
        df = df[df['title'].notna()]
        df = df.fillna(np.nan).replace([np.nan], [None])
        self.stdout.write('Populating database')
        for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            _, created = Movie.objects.get_or_create(
                title=row['title'],
                tagline=row['tagline'],
                overview=row['overview'],
                release_date=row['release_date'],
                homepage=row['homepage'],
                imdb_id=row['imdb_id'],
                adult=row['adult'],
                budget=row['budget'],
                genres=json.loads(row['genres'].replace("'", '"')),
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported %s' % options['csv_file']))
