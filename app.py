from flask import Flask, render_template, request, jsonify
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

app = Flask(__name__)

# Fetch dataset and initialize vectorizer and LSA
newsgroups = fetch_20newsgroups(subset='all')
documents = newsgroups.data

# Create TF-IDF matrix with the dataset
vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'), max_features=5000)
tfidf_matrix = vectorizer.fit_transform(documents)

# Apply SVD for dimensionality reduction
svd = TruncatedSVD(n_components=100)
reduced_matrix = svd.fit_transform(tfidf_matrix)

def search_engine(query):
    """
    Function to search for top 5 similar documents given a query.
    Input: query (str)
    Output: documents (list), similarities (list), indices (list)
    """
    # Transform the query using the same vectorizer and SVD
    query_vector = vectorizer.transform([query])
    query_vector_reduced = svd.transform(query_vector)

    # Compute cosine similarities between the query and the document vectors
    similarities = cosine_similarity(query_vector_reduced, reduced_matrix)[0]

    # Get indices of the top 5 similar documents
    top_indices = similarities.argsort()[-5:][::-1]
    top_similarities = similarities[top_indices]

    # Retrieve the corresponding documents
    top_documents = [documents[i] for i in top_indices]

    return top_documents, top_similarities.tolist(), top_indices.tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    documents, similarities, indices = search_engine(query)
    return jsonify({'documents': documents, 'similarities': similarities, 'indices': indices})

if __name__ == '__main__':
    app.run(debug=True)
