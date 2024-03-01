"""
Merges the AMLO and Homicides datasets
"""

import os
import pandas as pd
from datetime import datetime

DATA_PATH = "C:/Users/fdmol/Desktop/AMLO-NLP/src/data/"


FIRST_DATE = "20190101"
LAST_DATE = "20240227"


class DFParser:
    HOMICIDES_FILENAME = "homicidios_totales.csv"
    AMLO_SCORE_FILENAME = "xgb_agressivity_scores.csv"

    def __init__(self):
        self.homicides_df = pd.read_csv(
            os.path.join(DATA_PATH, self.HOMICIDES_FILENAME)
        )
        self.amlo_df = pd.read_csv(os.path.join(DATA_PATH, self.AMLO_SCORE_FILENAME))

    def transform_date(self, date):
        """
        This function transforms the date to the appropriate format
        """

        date = str(date)
        if len(date) == 8:
            date = datetime.strptime(date, "%d%m%Y")

        else:
            date = f"0{date}"
            date = datetime.strptime(date, "%d%m%Y")

        date = datetime.strftime(date, "%d%m%Y")

        return date

    def parse_homicides(self):
        """
        This function parses the homicides dataset
        """

        # Extract the date from the filename
        self.homicides_df["dates"] = self.homicides_df["dates"].apply(
            self.transform_date
        )

    def join_dfs(self):
        """
        This function joins the two dataframes
        """

        self.parse_homicides()

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
            how="inner",
        )

        # Drop the dates column
        self.df["date"] = self.df["date"].apply(
            lambda x: datetime.strptime(x, "%d%m%Y")
        )

        self.df.sort_values(by="date", inplace=True)

        self.df.drop(columns=["dates"], inplace=True)


if __name__ == "__main__":

    parser = DFParser()
    parser.join_dfs()

    parser.df.to_csv(os.path.join(DATA_PATH, "complete_datasets.csv"), index=False)

    print(parser.df.head())
