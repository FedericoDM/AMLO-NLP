"""
This script will process the PDFs and extract the total number of
homicides from them
"""

import re
import os

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

    def extract_text_from_pdf(self, pdf_file_path):
        """
        This function extracts the text from a PDF file
        """
        with open(pdf_file_path, "rb") as file:
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

            data = re.findall(r"Total(?:es)?\s+\d+", text_data)

            # Clean up the text to remove special characters (if needed)
            # text_data = re.sub(r'[^\w\s]', '', text_data)

            return data

    def get_total_homicides_government(self):
        """
        Get the total number of homicides from the government's PDFs
        """


if __name__ == "__main__":
    # Get the list of files
    HOMICIDIOS_GOB_PATH = os.path.join(DATA_PATH, "homicidios_gobierno/")
    HOMICIDIOS_ABIERTOS_PATH = os.path.join(DATA_PATH, "homicidios_abierto/")
    all_files_gob = os.listdir(HOMICIDIOS_GOB_PATH)
    all_files_abiertos = os.listdir(HOMICIDIOS_ABIERTOS_PATH)

    # Extract the text from each PDF
    for file_gob, file_abierto in zip(all_files_gob[:3], all_files_abiertos[:3]):
        if file_gob.endswith(".pdf"):
            text_gob = extract_text_from_pdf(
                os.path.join(HOMICIDIOS_GOB_PATH, file_gob)
            )
            print(text_gob)

        print("========================================")

        if file_abierto.endswith(".pdf"):
            text_abierto = extract_text_from_pdf(
                os.path.join(HOMICIDIOS_ABIERTOS_PATH, file_abierto)
            )
            print(text_abierto)
