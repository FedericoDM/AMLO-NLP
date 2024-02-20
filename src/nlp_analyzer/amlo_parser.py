import re
import os
from tqdm import tqdm


PATH = "C:/Users/fdmol/Desktop/AMLO-NLP/src/data/text_files/"
DIALOGUES_PATH = "C:/Users/fdmol/Desktop/AMLO-NLP/src/data/presidents_dialogues/"
REGEX_PATTERNS = [
    r"copyright derechos reservados 2011-2020 - sitio oficial de andrés manuel lópez obrador",
    r"versión estenográfica de la conferencia de prensa matutina del presidente de méxico, andrés manuel lópez obrador – amlo \| \d+/\d+/\d+",
    r" descarga audio: \d+-\d+-\d+ audio conferencia de prensa presidente de méxico palacio nacional,",
]

STOPWORDS = [
    "el",
    "ella",
    "ellos",
    "ellas",
    "con",
    "contra",
    "como",
    "de",
    "por",
    "para",
    "a",
    "ante",
    "bajo",
    "cabe",
    "con",
    "contra",
    "de",
    "desde",
    "durante",
    "en",
    "entre",
    "hacia",
    "hasta",
    "mediante",
    "para",
    "por",
    "según",
    "sin",
    "so",
    "sobre",
    "tras",
    "versus",
    "vía",
    "y",
    "e",
    "ni",
    "o",
    "u",
    "pero",
    "aunque",
    "la",
    "las",
    "los",
    "lo",
    "un",
    "una",
    "unos",
    "unas",
    "al",
    "del",
    "lo",
    "le",
    "les",
    "me",
    "te",
    "se",
    "nos",
    "os",
    "les",
    "le",
    "me",
    "te",
    "se",
    "nos",
    "que",
    "esta",
    "este",
    "estas",
    "estos",
    "porque",
    "si",
    "yo",
    "no",
    "le",
    "va",
    "ya",
    "es",
    "mil",
    "ciento",
    "tu",
    "ha",
    "he",
    "han",
    "sus",
    "su",
    "suyo",
    "suya",
    "suyos",
    "suyas",
]


PRESIDENT_REGEXES = [
    r"pregunta:.*",
    r"interlocutor:.*",
    r"intervención:.*",
    r"interlocutora:.*",
    r"voz hombre:.*",
    r"voz mujer:.*",
]


CHARS_TO_REMOVE = [
    ",",
    ".",
    "!",
    "?",
    "¡",
    "¿",
    "“",
    "”",
    ";",
    "-",
    "_",
    "—",
    "–",
    "•",
    "…",
    "(",
    ")",
    "[",
    "]",
]


class AMLOParser:
    REGEX_PATTERNS = REGEX_PATTERNS
    STOPWORDS = STOPWORDS
    PRESIDENT_REGEXES = PRESIDENT_REGEXES
    DIALOGUES_PATH = DIALOGUES_PATH
    CHARS_TO_REMOVE = CHARS_TO_REMOVE

    def __init__(self, path):
        self.path = path
        self.president_split = "presidente andrés manuel lópez obrador:"

    def txt_to_list(self, filename):
        """
        Add each line of a text file to a list
        """

        file_path = os.path.join(self.path, filename)
        lines = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().split()
                lines.append(line)

        return lines

    def file_to_string(self, filename):
        """
        Add each line of a text file to a string
        """
        text = ""
        file_path = os.path.join(self.path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                text += line

        text = text.strip()
        text = text.lower()
        text = re.sub(r"\s+", " ", text)

        # Remove commas, periods, and other special characters

        for pattern in self.REGEX_PATTERNS:
            text = re.sub(pattern, "", text)

        for char_to_remove in self.CHARS_TO_REMOVE:
            text = text.replace(char_to_remove, "")

        return text

    def remove_stopwords(self, text):
        """
        Removes predefined stopwords from a string
        """
        text = text.split()
        text = [word for word in text if word not in self.STOPWORDS]

        # Remove digits with regex
        text = [re.sub(r"\d+", "", word) for word in text]
        text = " ".join(text)
        return text

    def get_presidents_dialogues(self, filename, remove_stopwords=False):
        """
        Get the president's dialogues from a text file
        """
        text = self.file_to_string(filename)
        text = text.split(self.president_split)

        # Apply regex to only get the president's dialogues
        for regex in self.PRESIDENT_REGEXES:
            text = [re.sub(regex, "", line) for line in text]

        if remove_stopwords:
            text = [self.remove_stopwords(line) for line in text]

        text = [line.strip() for line in text if line.strip() != ""]

        return text

    def clean_text(self, text, remove_stopwords=False):
        """
        This function is used to clean a particular text with the
        rules defined in this class
        """
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        if remove_stopwords:
            text = self.remove_stopwords(text)

        for pattern in self.REGEX_PATTERNS:
            text = re.sub(pattern, "", text)

        return text

    def save_all_presidents_dialogues(self):
        """
        Save the president's dialogues to a text file
        """
        TEXT_INDEX = 1
        all_files = os.listdir(self.path)

        for file in tqdm(all_files):
            if file.endswith(".txt"):
                text = self.get_presidents_dialogues(file, remove_stopwords=True)
                file_path = os.path.join(self.DIALOGUES_PATH, file)
                file_path = file_path.replace(".txt", "_president_dialogues.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    for line in text[TEXT_INDEX:]:
                        f.write(line)
                        f.write("\n")


if __name__ == "__main__":
    parser = AMLOParser(PATH)
    parser.save_all_presidents_dialogues()
