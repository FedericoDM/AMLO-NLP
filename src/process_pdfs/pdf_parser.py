"""
This script will process the PDFs and extract the total number of
homicides from them
"""

import re
import os

from tqdm import tqdm
import pandas as pd
import PyPDF2


DATA_PATH = "C:/Users/fdmol/Desktop/AMLO-NLP/src/data/"


class PDFParser:
    """
    Extracts the PDFs and processes them
    """

    DATA_PATH = DATA_PATH

    def __init__(self) -> None:
        self.HOMICIDIOS_GOB_PATH = os.path.join(DATA_PATH, "homicidios_gobierno/")
        self.HOMICIDIOS_ABIERTOS_PATH = os.path.join(DATA_PATH, "homicidios_abierto/")

        self.all_files_gob = os.listdir(self.HOMICIDIOS_GOB_PATH)
        self.all_files_abiertos = os.listdir(self.HOMICIDIOS_ABIERTOS_PATH)

    def extract_homicides_from_pdf(self, pdf_file_path):
        """
        This function extracts the text from a PDF file
        """
        with open(pdf_file_path, "rb") as file:

            try:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)

                # Extract text from each page
                text_data = ""
                page = reader.pages[0]
                text_data += page.extract_text()

                # Extract text from each page
                text_data = ""
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text_data += page.extract_text()

                data = re.findall(r"Total(?:es)?:?\s+\d+", text_data)

                if data:
                    data = data[0]
                    data = re.findall(r"\d+", data)[0]

                else:
                    data = 0

            except Exception as e:
                print(f"Error with file {pdf_file_path}")
                data = None
                print(e)

        return data

    def get_total_homicides_government(self):
        """
        Get the total number of homicides from the government's PDFs
        """
        self.total_homicides_gov = []

        for file_gob in tqdm(self.all_files_gob):
            if file_gob.endswith(".pdf"):
                text_gob = self.extract_homicides_from_pdf(
                    os.path.join(self.HOMICIDIOS_GOB_PATH, file_gob)
                )

                self.total_homicides_gov.append(text_gob)

            else:
                self.total_homicides_gov.append(None)

    def get_total_homicides_abierto(self):
        """
        Get the total number of homicides from the abierto's PDFs
        """
        self.total_homicides_abierto = []

        for file_abierto in tqdm(self.all_files_abiertos):
            if file_abierto.endswith(".pdf"):
                text_abierto = self.extract_homicides_from_pdf(
                    os.path.join(self.HOMICIDIOS_ABIERTOS_PATH, file_abierto)
                )

                self.total_homicides_abierto.append(text_abierto)

            else:
                self.total_homicides_abierto.append(None)

    def create_table(self):
        """
        Create a table with the total homicides
        """
        # Extract dates from files

        dates = []
        for file_abierto in self.all_files_abiertos:
            file_split = file_abierto.split("_")
            date = file_split[1]

            # Date is DDMMYYYY, but we want it to be YYYYMMDD
            year = date[-4:]
            month = date[2:4]
            day = date[:2]
            date = f"{year}{month}{day}"

            dates.append(date)

        # Create the table
        table = pd.DataFrame(
            {
                "dates": dates,
                "homicidios_fuentes_gobierno": self.total_homicides_gov,
                "homicidios_fuentes_abiertas": self.total_homicides_abierto,
            }
        )

        return table


if __name__ == "__main__":
    # Get the list of files
    pdf_parser = PDFParser()
    print("Processing total homicides from government's PDFs")
    pdf_parser.get_total_homicides_government()
    print("Processing total homicides from open sources PDFs")
    pdf_parser.get_total_homicides_abierto()
    print("Creating table")
    table = pdf_parser.create_table()

    # Save the table
    table.to_csv(os.path.join(DATA_PATH, "homicidios_totales.csv"), index=False)
