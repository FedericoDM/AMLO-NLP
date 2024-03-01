"""
Processes the obtained dataframe from the PDF scraper
"""

import os
import re
import pandas as pd

DATA_PATH = "C:/Users/fdmol/Desktop/AMLO-NLP/src/data/"


class DFParser:
    FILENAME = "homicidios_totales.csv"

    def __init__(self) -> None:
        self.df = pd.read_csv(os.path.join(DATA_PATH, self.FILENAME))

    def find_digit(self, string):
        """
        Finds a digit in a string
        """
        return re.findall(r"\d+", string)

    def process_df(self):
        """
        Processes the dataframe
        """
        # Add zero as a value for NaN
        self.df.fillna(0, inplace=True)
