"""
This script is in charge of creating the Neural Network to predict
the aggressivity of the president's dialogues
"""

from collections import Counter

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

# Minmaxscaler
from sklearn.preprocessing import MinMaxScaler


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
    def __init__(
        self,
        num_epochs,
    ) -> None:
        self.num_epochs = num_epochs

    def train_model(self, vocab, train_loader):
        """
        This function wraps the entire training process: data loading, model creation,
        """
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model = NeuralRegressor(vocab_size=len(vocab) + 1, embedding_dim=100).to(device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        for epoch in range(self.num_epochs):
            model.train()

            for batch in train_loader:

                inputs, targets = (
                    batch  # Here, batch directly unpacks into inputs and targets
                )

                inputs, targets = inputs.to(device), targets.to(device)

                optimizer.zero_grad()
                outputs = model(inputs).squeeze(1)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()

            print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss.item():.4f}")
