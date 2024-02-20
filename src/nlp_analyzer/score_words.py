"""
This script is used to score all the words in the president's dialogues
using TF-IDF and then save the results to several CSV files
"""

import re
import os
import pandas as pd
from tqdm import tqdm

from sklearn.feature_extraction.text import TfidfVectorizer

from amlo_parser import AMLOParser


PATH = "C:/Users/fdmol/Desktop/AMLO-NLP/src/data/text_files/"
SCORES_PATH = "C:/Users/fdmol/Desktop/AMLO-NLP/src/data/word_scores/"


# Use TF-IDF to find the most important words in the text
def get_most_important_words(text, filename, save=False):
    # Create a TfidfVectorizer
    tfidf_vectorizer = TfidfVectorizer()

    # Apply the vectorizer
    tfidf_matrix = tfidf_vectorizer.fit_transform(text)

    # Print the result
    scores = tfidf_matrix.toarray()[0]
    words = tfidf_vectorizer.get_feature_names_out()

    # Create a DataFrame with the result
    df = pd.DataFrame({"Word": words, "Score": scores})
    df.sort_values("Score", ascending=False, inplace=True)

    if save:
        df.to_csv(filename, index=False)

    return df


if __name__ == "__main__":
    text_parser = AMLOParser(PATH)

    # List of all the text files
    all_files = os.listdir(PATH)

    # Get the president's dialogues from a text file
    for file in tqdm(all_files):
        if file.endswith(".txt"):
            text = text_parser.get_presidents_dialogues(file, remove_stopwords=True)
            new_file_path = os.path.join(SCORES_PATH, file)
            new_file_path = new_file_path.replace(".txt", "_word_scores.csv")
            get_most_important_words(text, new_file_path, save=True)
