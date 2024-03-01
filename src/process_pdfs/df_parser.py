"""
Merges the AMLO and Homicides datasets
"""

import os
import re
import pandas as pd

DATA_PATH = "C:/Users/fdmol/Desktop/AMLO-NLP/src/data/"


class DFParser:
    HOMICIDES_FILENAME = "homicidios_totales.csv"
    AMLO_SCORE_FILENAME = "xgb_agressivity_scores.csv"

    def __init__(self):
        self.homicides_df = pd.read_csv(
            os.path.join(DATA_PATH, self.HOMICIDES_FILENAME)
        )
        self.amlo_df = pd.read_csv(os.path.join(DATA_PATH, self.AMLO_SCORE_FILENAME))

    def process_df(self):
        pass


if __name__ == "__main__":

    parser = DFParser()
    parser.process_df()

    parser.df.to_csv(
        os.path.join(DATA_PATH, "homicidios_totales_clean.csv"), index=False
    )

    print(parser.df.head())
