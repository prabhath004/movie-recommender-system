import React, { useState } from 'react';
import './App.css';

const App = () => {
  const [movieTitle, setMovieTitle] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  // Backend URL configuration based on environment
  const backendUrl = process.env.NODE_ENV === 'production'
    ? 'https://www.movie-recommend.com ' // Use HTTPS in production
    : 'http://54.91.246.141:8000'; 
       // For local testing

  // Function to fetch recommendations from backend
  const fetchRecommendations = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${backendUrl}/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ movie_title: movieTitle, user_id: 1 }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch recommendations. Status: ${response.status}`);
      }

      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setRecommendations(data);
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Failed to fetch recommendations. Please try again later.');
    }
    setLoading(false);
  };

  // Function to fetch movie suggestions from backend
  const fetchMovieSuggestions = async (title) => {
    try {
      const response = await fetch(`${backendUrl}/suggestions?movie_title=${title}`);
      const data = await response.json();
      setSuggestions(data);
    } catch (err) {
      console.error('Error fetching suggestions:', err);
    }
  };

  // Input change handler with suggestion fetching logic
  const handleInputChange = (e) => {
    const input = e.target.value;
    setMovieTitle(input);
    if (input.length > 2) {
      fetchMovieSuggestions(input);
    } else {
      setSuggestions([]);
    }
  };

  // Form submit handler
  const handleSubmit = (e) => {
    e.preventDefault();
    setSuggestions([]);
    fetchRecommendations();
  };

  // Click handler for suggestions
  const handleSuggestionClick = (suggestion) => {
    setMovieTitle(suggestion);
    setSuggestions([]);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1 className="header">🎬 Welcome to MovieRecommender</h1>
        <h3>Discover recommendations for your favorite movies</h3>
      </header>

      <form onSubmit={handleSubmit} className="movie-form">
        <div className="search-container">
          <input
            type="text"
            value={movieTitle}
            onChange={handleInputChange}
            placeholder="Search for a movie..."
            required
            className="movie-input"
          />
          <button type="submit" className="search-button">GO</button>
        </div>

        {suggestions.length > 0 && (
          <ul className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <li key={index} onClick={() => handleSuggestionClick(suggestion)}>
                {suggestion}
              </li>
            ))}
          </ul>
        )}
      </form>

      {loading ? (
        <div className="loading-spinner">Loading recommendations...</div>
      ) : error ? (
        <p className="error-message">{error}</p>
      ) : recommendations.length > 0 ? (
        <div>
          <h2>Your Recommendations:</h2>
          <div className="movie-grid">
            {recommendations.map((movie, index) => (
              <div key={index} className="movie-card">
                <img
                  src={movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Image'}
                  alt={movie.title}
                  className="movie-poster"
                />
                <h3>{movie.title}</h3>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default App;
