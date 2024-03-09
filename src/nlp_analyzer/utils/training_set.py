"""
This class creates the corresponding training set for the labeled data
"""

import os
import re
import pandas as pd
from tqdm import tqdm
from utils.amlo_parser import AMLOParser
from utils.constants import TRAINING_PATH, LABELED_PATH, TEXT_FILES_PATH, DIALOGUES_PATH


# Read the labeled data
class TrainingSet:
    TRAINING_PATH = TRAINING_PATH
    LABELED_PATH = LABELED_PATH
    TEXT_FILES_PATH = TEXT_FILES_PATH
    DIALOGUES_PATH = DIALOGUES_PATH

    def __init__(self, remove_stopwords):
        self.amlo_parser = AMLOParser(self.TEXT_FILES_PATH)
        self.path = LABELED_PATH
        self.labeled_data, self.agressive_phrases = self.read_labeled_data()
        self.remove_stopwords = remove_stopwords

        self.labeled_conference_ids = self.labeled_data["conference_id"].unique()
        self.all_files = os.listdir(self.TEXT_FILES_PATH)

    def read_labeled_data(self):
        """
        Reads the labeled data and agressive phrases from the excel file
        """
        labeled_data = pd.read_excel(self.path, sheet_name="labels")
        agressive_phrases = pd.read_excel(self.path, sheet_name="frases_odio")

        labeled_data = labeled_data.dropna()
        labeled_data.reset_index(drop=True, inplace=True)

        return labeled_data, agressive_phrases

    def agressive_phrases_to_txt(self, agressive_phrases, conference_id):
        """
        Parses the utterances from the dataframe and saves them to a txt file
        """
        # Save the agressive phrases to a txt file
        agressive_phrases_df = agressive_phrases.loc[
            agressive_phrases["conference_id"] == conference_id, :
        ]

        agressive_phrases_df.reset_index(drop=True, inplace=True)
        agressive_phrases_df = agressive_phrases_df.loc[:, ["phrase"]]

        # Write the text to a file
        new_file_path = os.path.join(self.TRAINING_PATH, f"{conference_id}.txt")
        new_file_path = new_file_path.replace(".txt", "_agressive_phrases.txt")

        with open(new_file_path, "w", encoding="utf-8") as f:
            for index, row in agressive_phrases_df.iterrows():
                phrase = self.amlo_parser.clean_text(
                    row["phrase"], remove_stopwords=self.remove_stopwords
                )
                f.write(phrase + "\n")

    def non_agressive_to_txt(self, conference_id):
        """
        Copies the non-agressive phrases to a txt file. Such phrases are under the
        president's dialogues folder
        """
        # Save the non-agressive phrases to a txt file
        print(f"Conference {conference_id} is not agressive")
        # Copy file to training data
        dialogue_path = os.path.join(
            self.DIALOGUES_PATH, f"{conference_id}_president_dialogues.txt"
        )

        with open(dialogue_path, "r", encoding="utf-8") as f:
            text = f.read()
            text = self.amlo_parser.clean_text(
                text, remove_stopwords=self.remove_stopwords
            )

        new_file_path = os.path.join(
            self.TRAINING_PATH, f"{conference_id}_non_agressive.txt"
        )

        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(text)

    def create_training_set(self):
        for file in tqdm(self.all_files):
            if file.endswith(".txt"):
                conference_id = int(re.findall(r"\d+", file)[0])

                if conference_id in self.labeled_conference_ids:
                    # Get conference label
                    conference_label = self.labeled_data.loc[
                        self.labeled_data["conference_id"] == conference_id,
                        "is_agressive",
                    ].values[0]

                    if conference_label == 1:
                        # Get the agressive phrases
                        self.agressive_phrases_to_txt(
                            self.agressive_phrases, conference_id
                        )
                    else:
                        # Copy the file to the training data
                        self.non_agressive_to_txt(conference_id)
                else:
                    continue
