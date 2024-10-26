import pandas as pd
import numpy as np
import ast
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split

# Load the datasets
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

# Merge movies and credits data on the 'title' column
movies = movies.merge(credits, on='title')

# Select relevant columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

# Helper functions to convert JSON-like columns into lists
def convert(obj):
    return [i['name'] for i in ast.literal_eval(obj)]

def convert3(obj):
    return [i['name'] for i in ast.literal_eval(obj)[:3]]

def director_f(obj):
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            return [i['name']]
    return []

# Apply the helper functions to relevant columns
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(director_f)

# Process the 'overview' and other text columns
movies['overview'] = movies['overview'].apply(lambda x: x.split())
movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ", "") for i in x])

# Create a 'tags' column
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Prepare a new DataFrame for recommendations
new_df = movies[['movie_id', 'title', 'tags']]
new_df.loc[:, 'tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())  # Avoid SettingWithCopyWarning

# Create feature vectors for content-based recommendations
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()

# Compute cosine similarity for content-based recommendations
similarity = cosine_similarity(vectors)

# Content-based recommendation function
def recommend_content_based(movie_title, n=5):
    if movie_title not in new_df['title'].values:
        return f"Error: '{movie_title}' not found in the database."
    movie_index = new_df[new_df['title'] == movie_title].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n+1]
    return [new_df.iloc[i[0]].title for i in movie_list]

# Simulate user-movie ratings
ratings_data = {
    'user_id': np.random.randint(1, 11, size=50),
    'movie_id': np.random.randint(1, 21, size=50),
    'rating': np.random.randint(1, 6, size=50)
}
ratings_df = pd.DataFrame(ratings_data)

# Set up Surprise's collaborative filtering model
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'movie_id', 'rating']], reader)
trainset, testset = train_test_split(data, test_size=0.2)
svd = SVD()
svd.fit(trainset)

# Collaborative filtering recommendation function
def recommend_collaborative(user_id, movie_ids, algo, n=5):
    predictions = [algo.predict(user_id, movie_id) for movie_id in movie_ids]
    top_predictions = sorted(predictions, key=lambda x: x.est, reverse=True)[:n]
    return [pred.iid for pred in top_predictions]

# Hybrid recommendation function
def hybrid_recommendation(user_id, movie_title, n=5, weight_content=0.6, weight_collab=0.4):
    content_recs = recommend_content_based(movie_title, n=n)
    if isinstance(content_recs, str):
        return content_recs

    input_movie = new_df[new_df['title'] == movie_title]
    if input_movie.empty:
        return f"Error: '{movie_title}' not found."

    movie_genre = input_movie['tags'].values[0].lower()
    all_movie_ids = ratings_df['movie_id'].unique()
    collab_movie_ids = recommend_collaborative(user_id, all_movie_ids, svd, n=15)

    collab_recs = []
    for movie_id in collab_movie_ids:
        movie_row = new_df[new_df['movie_id'] == movie_id]
        if not movie_row.empty and movie_genre in movie_row['tags'].values[0].lower():
            collab_recs.append(movie_row['title'].values[0])

    random.shuffle(collab_recs)
    final_recs = list(set(content_recs * int(weight_content * 10) + collab_recs * int(weight_collab * 10)))
    return list(dict.fromkeys(final_recs))[:n]
