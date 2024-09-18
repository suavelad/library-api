
import pandas as pd
import requests
from io import StringIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity





# Function to recommend books
def recommend_books(title):

    # Load the dataset

    # data = pd.read_json('https://www.kaggle.com/datasets/opalskies/large-books-metadata-dataset-50-mill-entries/books.json')

    url = 'https://www.kaggle.com/code/mamudukamilo/notebookfdc5182903/input/large-books-metadata-dataset-50-mill-entries/books.json/books.json'

    # Make a request to the URL with SSL verification disabled
    response = requests.get(url, verify=False)

    # Convert the content to a StringIO object and read it into pandas
    data = pd.read_json(StringIO(response.text))

    data['Features'] = data['author_name']

    vectorizer = TfidfVectorizer(stop_words='english')

    tfidf_matrix = vectorizer.fit_transform(data['Features'])

    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Get the index of the book that matches the title
    idx = data[data['title'] == title].index[0]

    # Get similarity scores for all books
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the books based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the indices of the top 5 most similar books (excluding the first one which is the input book itself)
    sim_scores = sim_scores[1:6]

    # Get the book indices
    book_indices = [i[0] for i in sim_scores]

    # Return the top 5 most similar books
    return data['title'].iloc[book_indices]

