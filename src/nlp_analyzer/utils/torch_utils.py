"""
This file defines several utility functions for working with PyTorch.
"""

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


class AggressivityDataset(Dataset):
    def __init__(self, texts, vocab, scores=None):
        """
        texts: List of text data
        vocab: A dictionary mapping tokens to indices
        scores: List of aggressivity scores (for training data); None for unseen data
        """
        self.texts = [self.numericalize(text, vocab) for text in texts]
        self.scores = scores

    def numericalize(self, text, vocab):
        # Simple tokenization and numericalization based on the provided vocab
        tokenized = (
            text.lower().split()
        )  # Simple whitespace tokenization, adjust as needed
        return [
            vocab.get(token, 0) for token in tokenized
        ]  # 0 as the index for unknown words

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        item = {"text": self.texts[idx]}
        if self.scores is not None:  # Handle cases where scores might not be available
            item["score"] = self.scores[idx]
        return item


class DataPreprocessor:

    def __init__(self, vocab, tokenizer, training_df, unseen_df, min_freq=1):
        self.vocab = vocab
        self.tokenizer = tokenizer
        self.min_freq = min_freq

    def build_vocab(texts, tokenizer, min_freq=1):
        """
        Builds a vocabulary from the given texts based on frequency.

        Args:
        - texts (list of str): List of text samples.
        - tokenizer (callable): Function to tokenize text.
        - min_freq (int): Minimum frequency for a word to be included in the vocab.

        Returns:
        - vocab (dict): Mapping of word to unique index.
        """
        # Tokenize all texts and count word frequencies
        counter = Counter(token for text in texts for token in tokenizer(text))

        # Filter words by min_freq and assign unique indices
        vocab = {
            word: i + 2
            for i, (word, freq) in enumerate(counter.items())
            if freq >= min_freq
        }  # Start indexing from 2

        # Special tokens
        vocab["<pad>"] = 0  # Padding token
        vocab["<unk>"] = 1  # Unknown word token

        return vocab

    # Example tokenizer function
    def tokenizer(text):
        return text.split()

    # Functions
    def collate_fn(batch):
        text_sequences = [
            torch.tensor(item["text"], dtype=torch.long) for item in batch
        ]  # Ensure conversion to tensor
        # Check if 'score' key exists and handle accordingly
        scores = (
            torch.tensor([item["score"] for item in batch], dtype=torch.float)
            if "score" in batch[0]
            else None
        )

        text_sequences_padded = pad_sequence(
            text_sequences, batch_first=True, padding_value=0
        )

        return (
            (text_sequences_padded, scores)
            if scores is not None
            else text_sequences_padded
        )
