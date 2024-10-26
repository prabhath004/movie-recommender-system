from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import ast
import random
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split, cross_validate

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# TMDB API Key
TMDB_API_KEY = '07e4b18ff9a853fec7d2fc25c1d6da46'

# Load the datasets
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

# Merge datasets and clean up
movies = movies.merge(credits, on='title')
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

# Helper functions for data processing
def convert(obj):
    return [i['name'] for i in ast.literal_eval(obj)]

def convert3(obj):
    return [i['name'] for i in ast.literal_eval(obj)[:3]]

def director_f(obj):
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            return [i['name']]
    return []

# Apply helper functions
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(director_f)

# Process text columns for tags
movies['overview'] = movies['overview'].apply(lambda x: x.split())
movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ", "") for i in x])

# Create a 'tags' column
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
new_df = movies[['movie_id', 'title', 'tags']]
new_df['title'] = new_df['title'].apply(lambda x: x.lower())
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())

# Create content-based recommendation vectors
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()
similarity = cosine_similarity(vectors)

# Simulate user-movie ratings for collaborative filtering
ratings_data = {
    'user_id': np.random.randint(1, 11, size=50),
    'movie_id': np.random.randint(1, 21, size=50),
    'rating': np.random.randint(1, 6, size=50)
}
ratings_df = pd.DataFrame(ratings_data)

# Setup collaborative filtering model using Surprise library
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'movie_id', 'rating']], reader)
trainset, testset = train_test_split(data, test_size=0.2)
svd = SVD()
svd.fit(trainset)

# Recommendation Functions
def recommend_content_based(movie_title, n=5):
    movie_title = movie_title.lower()
    if movie_title not in new_df['title'].values:
        return f"Error: '{movie_title}' not found in the database."
    idx = new_df[new_df['title'] == movie_title].index[0]
    distances = similarity[idx]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n+1]
    return [new_df.iloc[i[0]].title for i in movie_list]

def recommend_collaborative(user_id, movie_ids, algo, n=5):
    predictions = [algo.predict(user_id, movie_id) for movie_id in movie_ids]
    top_predictions = sorted(predictions, key=lambda x: x.est, reverse=True)[:n]
    return [pred.iid for pred in top_predictions]

def hybrid_recommendation(user_id, movie_title, n=5, weight_content=0.6, weight_collab=0.4):
    content_recs = recommend_content_based(movie_title, n)
    collab_recs = recommend_collaborative(user_id, ratings_df['movie_id'].unique(), svd, n)
    final_recs = list(set(content_recs * int(weight_content * 10) + collab_recs * int(weight_collab * 10)))
    random.shuffle(final_recs)
    return final_recs[:n]

def fetch_poster(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    try:
        data = requests.get(url).json()
        if data['results']:
            poster_path = data['results'][0]['poster_path']
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except requests.RequestException as e:
        app.logger.error(f"Error fetching poster: {e}")
    return None

# Routes
@app.route('/')
def home():
    return "Welcome to the Movie Recommendation API!"

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    movie_title = data.get('movie_title', '').strip()
    user_id = data.get('user_id', 1)

    if not movie_title:
        return jsonify({"error": "movie_title parameter is required"}), 400

    recommendations = hybrid_recommendation(user_id, movie_title, n=5)
    results = [{"title": rec, "poster_url": fetch_poster(rec)} for rec in recommendations]
    return jsonify(results)

@app.route('/suggestions', methods=['GET'])
def suggestions():
    partial_title = request.args.get('movie_title', '').strip().lower()
    matches = new_df[new_df['title'].str.contains(partial_title)].head(5)['title'].tolist()
    return jsonify(matches)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
