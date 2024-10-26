🎬 Movie Recommender System
A Movie Recommender System that suggests movies using content-based filtering, collaborative filtering, and a hybrid model. It also shows movie posters fetched from TMDB API. The backend runs on Flask, and the frontend is built with React.


🛠️ Tech Stack
Frontend: React.js
Backend: Flask (Python)
ML Models: Scikit-learn & Surprise Library
API: TMDB API for movie posters
Hosting:
Backend: AWS EC2
Frontend: AWS S3 + CloudFront

🌐 Deployment
Backend:
Host the backend on AWS EC2.
Use Gunicorn + Nginx for production.
Frontend:

Upload the React build folder to S3.
Serve it with CloudFront.

🚀 Try it Out
Localhost : http://localhost:3000/
Live Website : www.movie-recommend.com


📊 Models Used
Content-based filtering: Suggests similar movies based on genres, keywords, and casts.
Collaborative filtering: Uses the Surprise library to predict user preferences.
Hybrid model: Combines both models for better recommendations.

🛡️ CORS Configuration
CORS is enabled to allow the frontend to communicate with the backend.


👨‍💻 Author
Developed by Your Prabhath Palakurthi.




