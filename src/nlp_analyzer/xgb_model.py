"""
Script to train the XGBoost model 
"""

import re
import pandas as pd
import os
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split


from sklearn.preprocessing import MinMaxScaler

from sklearn.metrics import mean_squared_error, r2_score

import xgboost as xgb

# Local imports
from src.nlp_analyzer.training_set import TrainingSet


class XGBoost:
    def __init__(self, folder_path, dialogues_path):
        self.dialogues_path = dialogues_path
        self.folder_path = folder_path
        self.training_set = TrainingSet(remove_stopwords=True)

    def create_regression_training_df(self):
        """
        Creates a DataFrame with the training data for the classification model
        """

        # Initialize an empty list to store data
        data = []

        # Iterate through each file in the folder
        for file in os.listdir(self.folder_path):
            if file.endswith(".txt"):
                # Determine the label based on the file name
                label = 0 if "non" in file else 1
                id = int(re.findall(r"\d+", file)[0])
                # Read the text file
                with open(
                    os.path.join(self.folder_path, file), "r", encoding="utf-8"
                ) as f:
                    text = f.read()
                    # Get text from president's dialogues
                    with open(
                        os.path.join(
                            self.dialogues_path, f"{id}_president_dialogues.txt"
                        ),
                        "r",
                        encoding="utf-8",
                    ) as f:
                        dialogues = f.read()

                if label == 1:
                    # Ratio of agressive phrases
                    length_agressive = len(text.split())
                    length_total = len(dialogues.split())

                    ratio = length_agressive / length_total

                    data.append({"id": id, "text": text, "score": ratio})

                else:

                    data.append({"id": id, "text": dialogues, "score": 0})

        # Convert the list to a DataFrame
        self.training_df = pd.DataFrame(data)

    def create_unseen_df(training_set, df):
        """
        This function creates a DataFrame with the conferences
        that have not been labeled yet
        """
        # Now, let us do it for the entire dataset
        data = []

        labeled_ids = df["id"].values

        # Iterate through each file in the folder
        for file in os.listdir(training_set.DIALOGUES_PATH):
            if file.endswith(".txt"):
                # Determine the label based on the file name
                conference_id = int(re.findall(r"\d+", file)[0])

                if conference_id not in labeled_ids:
                    # Read the text file
                    with open(
                        os.path.join(training_set.DIALOGUES_PATH, file),
                        "r",
                        encoding="utf-8",
                    ) as f:
                        text = f.read()
                        data.append({"id": conference_id, "text": text})

        unseen_df = pd.DataFrame(data)

        return unseen_df

    def train_xgboost(self):
        """
        Trains an XGBoost model to predict
        the score of agressivity
        """

        # Import the XGBoost library
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)

        # Fit and transform the 'text' column
        X = self.tfidf_vectorizer.fit_transform(self.training_df["text"])

        # Assuming 'label' is your target variable
        y = self.training_df["score"]

        # Assuming `X` is your matrix of embeddings and `y` is
        # your vector of normalized aggressivity scores
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        # Create the DMatrix
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)

        # Define the parameters
        param = {
            "max_depth": 8,
            "eta": 0.15,
            "objective": "reg:squarederror",
            "eval_metric": "rmse",
        }

        # Train the model
        num_round = 250
        self.model = xgb.train(param, dtrain, num_round)

        # Make predictions
        y_pred = self.model.predict(dtest)

        # Evaluate the model
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"Mean Squared Error: {mse}")
        print(f"R^2 Score: {r2}")

    def predict_xgboost(self, unseen_df):
        """
        Predicts the labels for the unseen data
        """
        # Fit and transform the 'text' column
        X_unseen = self.tfidf_vectorizer.fit_transform(unseen_df["text"])

        # Create the DMatrix
        d_unseen = xgb.DMatrix(X_unseen)

        # Make predictions
        y_unseen = self.model.predict(d_unseen)

        # Add the predictions to the DataFrame
        unseen_df["score"] = y_unseen

        return unseen_df

    def train_all(self):
        """
        Trains the model and predicts the unseen data
        """
        self.create_regression_training_df()
        self.train_xgboost()
        unseen_df = self.create_unseen_df(self.training_set, self.training_df)
        results_df = self.predict_xgboost(unseen_df)

        complete_df = pd.concat([self.training_df, results_df], ignore_index=True)

        scaler = MinMaxScaler()
        # Normalize the score
        scores = np.array(complete_df["score"]).reshape(-1, 1)
        scaler.fit(scores)
        complete_df["score"] = scaler.transform(scores)

        # Add a column with the length of the text
        complete_df["num_words"] = complete_df["text"].apply(lambda x: len(x.split()))

        # Save the complete DataFrame
        return complete_df
