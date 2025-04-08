from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load your CSV
df = pd.read_csv("Reviews.csv")
print("🧠 Column names:", df.columns.tolist())

# Normalize column names (remove extra spaces)
df.columns = [col.strip() for col in df.columns]

# Try to find the genre column, regardless of capitalization
genre_col = next((col for col in df.columns if col.strip().lower() == "genre"), None)

@app.route('/genre/<genre>')
def get_genre_data(genre):
    if not genre_col:
        return jsonify({"error": "Genre column not found in dataset"}), 500

    genre_df = df[df[genre_col].str.lower() == genre.lower()].copy()

    if genre_df.empty:
        return jsonify([])

    numeric_fields = {
        'Pitchfork': 'pitchfork',
        'Metacritic (/10)': 'metacritic',
        'Anthony Fantano': 'fantano',
        'Release Year': 'release_year'
    }

    for col in numeric_fields:
        if col in genre_df.columns:
            genre_df[col] = pd.to_numeric(genre_df[col], errors='coerce')

    genre_df.dropna(subset=numeric_fields.keys(), inplace=True)

    result = []
    for artist, group in genre_df.groupby('Artist'):
        albums = group.sort_values('Release Year').to_dict(orient='records')
        for album in albums:
            for original_col, clean_key in numeric_fields.items():
                album[clean_key] = album[original_col]
        result.append({"artist": artist, "albums": albums})

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
