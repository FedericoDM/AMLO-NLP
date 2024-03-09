"""
This script is in charge of creating the Neural Network to predict
the aggressivity of the president's dialogues
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# Minmaxscaler
from sklearn.preprocessing import MinMaxScaler

from utils.constants import DATA_PATH, NUM_EPOCHS, EMBEDDING_DIM


# Classes and functions
class NeuralRegressor(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(NeuralRegressor, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.fc = nn.Linear(embedding_dim, 1)

    def forward(self, x):
        embedded = self.embedding(x)
        pooled = F.avg_pool2d(embedded, (embedded.shape[1], 1)).squeeze(
            1
        )  # Average pooling
        output = self.fc(pooled)
        return output


class NeuralTrainer:
    NUM_EPOCHS = NUM_EPOCHS
    EMBEDDING_DIM = EMBEDDING_DIM

    def __init__(
        self,
        vocab,
        train_loader,
        unseen_loader,
        training_df,
        unseen_df,
    ) -> None:
        self.vocab = vocab
        self.train_loader = train_loader
        self.unseen_loader = unseen_loader
        self.training_df = training_df
        self.unseen_df = unseen_df

    def train_model(self):
        """
        This function wraps the entire training process: data loading,
        model creation and training.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Instantiate model, loss and optimizer
        self.model = NeuralRegressor(
            vocab_size=len(self.vocab) + 1, embedding_dim=self.EMBEDDING_DIM
        ).to(self.device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        for epoch in range(self.NUM_EPOCHS):
            self.model.train()

            for batch in self.train_loader:

                inputs, targets = batch
                inputs, targets = inputs.to(self.device), targets.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(inputs).squeeze(1)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()

            print(f"Epoch {epoch+1}/{self.num_epochs}, Loss: {loss.item():.4f}")

    def predict_unseen_data(self):
        """
        Predicts the labels for the unseen data.
        """

        self.model.to(self.device)
        self.model.eval()
        with torch.no_grad():
            self.predictions = []
            for inputs in self.unseen_loader:  # No targets here
                inputs = inputs.to(
                    self.device
                )  # Ensure inputs are on the correct device
                outputs = self.model(inputs).squeeze(1)
                self.predictions.extend(outputs.cpu().numpy())

    def scale_data(self):
        """
        Scales the predictions and saves the DataFrame
        """
        self.unseen_df["score"] = self.predictions

        self.nnet_agressivity_scores = pd.concat(
            [self.training_df, self.unseen_df], axis=0
        )

        scaler = MinMaxScaler()
        # Normalize the score
        scores = np.array(self.nnet_agressivity_scores["score"]).reshape(-1, 1)
        scaler.fit(scores)
        self.nnet_agressivity_scores["score"] = scaler.transform(scores)
        self.nnet_agressivity_scores.to_csv(
            f"{DATA_PATH}nnet_agressivity_scores.csv", index=False
        )
