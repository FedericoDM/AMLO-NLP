"""
Merges the AMLO and Homicides datasets
"""

import os
import pandas as pd
from datetime import datetime

DATA_PATH = "C:/Users/fdmol/Desktop/AMLO-NLP/src/data/"


class DFParser:
    HOMICIDES_FILENAME = "homicidios_totales.csv"
    AMLO_SCORE_FILENAME = "xgb_agressivity_scores.csv"

    def __init__(self):
        self.homicides_df = pd.read_csv(
            os.path.join(DATA_PATH, self.HOMICIDES_FILENAME)
        )
        self.amlo_df = pd.read_csv(os.path.join(DATA_PATH, self.AMLO_SCORE_FILENAME))

    def join_dfs(self):
        """
        This function joins the two dataframes
        """

        self.homicides_df["dates"] = self.homicides_df["dates"].astype(str)

        print(self.homicides_df.head())
        print(self.amlo_df.head())

        self.amlo_df["id"] = self.amlo_df["id"].astype(str)

        self.amlo_df["date"] = self.amlo_df["id"].apply(
            lambda x: datetime.strptime(x, "%Y%m%d")
        )

        # Back to string, with %d%m%Y format

        self.amlo_df["date"] = self.amlo_df["date"].apply(
            lambda x: datetime.strftime(x, "%d%m%Y")
        )

        # Merge the dataframes

        self.df = pd.merge(
            self.amlo_df,
            self.homicides_df,
            left_on="date",
            right_on="dates",
            how="left",
        )

        # Drop the dates column
        self.df.drop(columns=["dates"], inplace=True)


if __name__ == "__main__":

    parser = DFParser()
    parser.join_dfs()

    parser.df.to_csv(os.path.join(DATA_PATH, "complete_datasets.csv"), index=False)

    print(parser.df.head())
