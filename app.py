import streamlit as st
import pickle
import pandas as pd
import requests


# --- HELPER FUNCTIONS (No changes needed) ---
def fetch_details(movie_id):
    try:
        api_key = "8265bd1679663a7ea12ac168da84d2e8"  # Your TMDb API Key
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = "https://image.tmdb.org/t/p/w500" + data.get('poster_path', '') if data.get('poster_path') else ""
        release_year = data.get('release_date', 'N/A')[:4]
        rating = round(data.get('vote_average', 0), 1)
        return data.get('title'), poster_path, release_year, rating
    except Exception:
        return None, None, None, None


def recommend(movie_title):
    try:
        movie_index = movies[movies['title'] == movie_title].index[0]
    except IndexError:
        return []
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies_data = [fetch_details(movies.iloc[i[0]].id) for i in movies_list]
    return [data for data in recommended_movies_data if all(data)]


# --- DATA LOADING ---
try:
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error(
        "Model files not found. Please make sure 'movies_dict.pkl' and 'similarity.pkl' are in the same directory.")
    st.stop()

# --- PAGE CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="CineSuggest")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
html, body, [class*="st-"] { font-family: 'Poppins', sans-serif; }
.main { background-color: #0d1117; }
.title { font-size: 3.5rem; font-weight: 700; color: #ffffff; text-align: center; padding: 1rem 0; }
.subtitle { font-size: 1.2rem; color: #a0aec0; text-align: center; margin-bottom: 2rem; }
.stButton > button {
    width: 100%; background: linear-gradient(90deg, #4F46E5, #8B5CF6); color: white; border: none;
    padding: 0.75rem 1.5rem; border-radius: 10px; font-size: 1.1rem; font-weight: bold;
    transition: all 0.3s ease-in-out; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3); }
.recommendation-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1.5rem; }
@media (max-width: 1200px) { .recommendation-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px) { .recommendation-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .recommendation-grid { grid-template-columns: repeat(1, 1fr); } }
.card-container {
    background-color: #1a202c; border-radius: 15px; padding: 1rem;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); display: flex; flex-direction: column;
}
.card-container:hover { transform: translateY(-10px); box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
.card-container img { border-radius: 10px; width: 100%; object-fit: cover; margin-bottom: 0.75rem; }
.movie-title-card { font-size: 1rem; font-weight: 600; color: #e2e8f0; text-align: center; flex-grow: 1; }
.movie-details { font-size: 0.85rem; color: #a0aec0; margin-top: 0.5rem; display: flex; align-items: center; justify-content: center; gap: 0.75rem; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- UI LAYOUT ---
st.markdown('<div class="title">🎬 CineSuggest</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Discover movies you\'ll love.</div>', unsafe_allow_html=True)

# Center the selectbox and button
_, mid_col, _ = st.columns([3, 1.5, 3])
with mid_col:
    selected_movie_name = st.selectbox('Select a movie:', movies['title'].values, label_visibility="collapsed")
    recommend_button = st.button('✨ Get Recommendations', use_container_width=True)

# --- RENDERING LOGIC ---
if recommend_button:
    recommendations = []

    # Create a temporary centered layout for the spinner
    with st.container():
        _, spinner_col, _ = st.columns([3, 1.5, 3])
        with spinner_col:
            with st.spinner('Curating recommendations for you...'):
                recommendations = recommend(selected_movie_name)

    # Display results in the main layout after the spinner is done
    if recommendations:
        st.write("---")
        st.subheader("You might also like:")

        cards_html = []
        for title, poster, year, rating in recommendations:
            if poster:
                card_html = f'<div class="card-container"><img src="{poster}" alt="{title} Poster"><p class="movie-title-card">{title}</p><div class="movie-details"><span>⭐ {rating}</span><span>🗓️ {year}</span></div></div>'
                cards_html.append(card_html)

        st.write(f'<div class="recommendation-grid">{"".join(cards_html)}</div>', unsafe_allow_html=True)

# Footer
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #a0aec0;'>Machine Learning Project &nbsp;&nbsp;|&nbsp;&nbsp; Movie Data from TMDb</p>",
    unsafe_allow_html=True)