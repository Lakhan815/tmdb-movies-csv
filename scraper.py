import os
import requests
import csv
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
ACCESS_KEY = os.getenv('ACCESS_TOKEN')

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {ACCESS_KEY}"
}

def funkyChars(text):
    if not text:
        return False
    encoding_markers = ['Ã', 'â', 'Â', 'Ã©', 'Ã±', 'Ã´', 'Ã¨', 'Ã¡']
    return any(marker in text for marker in encoding_markers)

def is_valid(movie):
    title = movie.get('title', '')
    overview = movie.get('overview', '')

    if funkyChars(title):
        print(f"  Skipping due to encoding issue: {title}")
        return False
    
    if funkyChars(overview):
        print(f"  Skipping due to encoding issue in overview: {title}")
        return False
    
    if not title.strip() or not movie.get('release_date'):
        return False
    
    return True
    
def cleaned_data(movie):
    cleaned = {
        'id': movie.get('id', ''),
        'title': movie.get('title', 'Unknown').strip(),
        'release_date': movie.get('release_date', 'N/A'),
        'vote_average': round(movie.get('vote_average', 0), 1),
        'popularity': round(movie.get('popularity', 0), 2),
        'language': movie.get('original_language', 'unknown').upper(),
        'overview': movie.get('overview', '').strip().replace('\n', ' '),
    }
    
    return cleaned

all_movies = []

#change this to change the amount of pages DO NOT FORGET 
num_pages=50

for page in range(1, num_pages +1):
    print (f"fetching page {page}")
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/popular",
        headers=headers,
        params={
            "language": "en-US",
            "page": page
        }
        )

    if response.status_code == 200:
        data = response.json()
        movies = [m for m in data['results'] if is_valid(m)]
        all_movies.extend(movies)
    else:
        print(f"Error on page {page}: {response.text}")
        break

print(f"\nTotal movies fetched: {len(all_movies)}")

with open('popular_movies.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldNames = ['id','title','release_date','vote_average','popularity','language','overview']
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
    writer.writeheader()

    for movie in all_movies:
        cleaned_movie = cleaned_data(movie)
        writer.writerow(cleaned_movie)

print(f"Exported {len(all_movies)} movies to 'popular_movies.csv'")