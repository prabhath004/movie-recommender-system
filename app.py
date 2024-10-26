from flask import Flask, request, jsonify
from movierecommentation import hybrid_recommendation

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Movie Recommendation API. Use /recommend to get recommendations."

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        movie_title = data.get('movie_title', '')
        user_id = data.get('user_id', 1)
        recommendations = hybrid_recommendation(user_id=user_id, movie_title=movie_title, n=5)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# No need for app.run() since Gunicorn will manage the application.
