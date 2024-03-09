"""
This script is in charge of creating the Neural Network to predict
the aggressivity of the president's dialogues
"""

import os
from collections import Counter

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.nn.utils.rnn import pad_sequence
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
