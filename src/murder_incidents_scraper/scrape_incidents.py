"""
This script will scrape the murder incidents in Mexico
"""

import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


URL = "http://www.informeseguridad.cns.gob.mx/"
HEADERS = {
    "Connection": "keep-alive",
    "Host": "www.informeseguridad.cns.gob.mx",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
}


class IncidentScraper:
    URL = URL

    def __init__(self):
        self.headers = HEADERS

    def get_table(self):
        """
        Gets table from the page
        """

        r = requests.get(self.URL, headers=self.headers)
        soup = BeautifulSoup(r.content, "html.parser")
        html_table = soup.find("table", {"class": "table table-striped"})

        # Find urls
        a_tags = html_table.find_all("a", {"target": "_blank"})

        homicidios_fuentes_gobierno = []
        homicidios_fuentes_abiertas = []

        for a_tag in a_tags:
            href = a_tag["href"]

            if "homicidios" in href:
                if "v2" in href:
                    homicidios_fuentes_gobierno.append(href)

                elif "jpg" in href:
                    homicidios_fuentes_gobierno.append(href)

                else:
                    homicidios_fuentes_abiertas.append(href)

        # Get the table
        min_length = min(
            len(homicidios_fuentes_gobierno), len(homicidios_fuentes_abiertas)
        )
        homicidios_fuentes_gobierno = homicidios_fuentes_gobierno[:min_length]
        homicidios_fuentes_abiertas = homicidios_fuentes_abiertas[:min_length]

        dates = [
            re.findall(r"\d+", homicide)[0] for homicide in homicidios_fuentes_gobierno
        ]

        # Create the table
        table = pd.DataFrame(
            {
                "dates": dates,
                "homicidios_fuentes_gobierno": homicidios_fuentes_gobierno,
                "homicidios_fuentes_abiertas": homicidios_fuentes_abiertas,
            }
        )

        # Construct urls
        table["homicidios_fuentes_gobierno"] = table[
            "homicidios_fuentes_gobierno"
        ].apply(lambda x: URL + x)
        table["homicidios_fuentes_abiertas"] = table[
            "homicidios_fuentes_abiertas"
        ].apply(lambda x: URL + x)

        self.table = table


if __name__ == "__main__":

    incindent_scraper = IncidentScraper()

    incindent_scraper.get_table()

    print(incindent_scraper.table)

    incindent_scraper.table.to_csv("homicidios.csv", index=False)
