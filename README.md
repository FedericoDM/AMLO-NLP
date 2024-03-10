# AMLO - Natural Language Processing Analysis

This repository contains the code and data for the analysis of the natural language processing of the Mexican President Andrés Manuel López Obrador (AMLO). The analysis is based on the speeches and press conferences of the president that are uploaded everyday to his own [website](src/amlo_scraper/scrape_amlo.py).

I created an 'aggressivity score' to measure how hostile he is on his morning conferences. For this, my team and me created a small dataset and extracted the 'aggressive sentences' from the speeches. 

**Disclaimer**: _This is a personal project and the results are not intended to be used for any political or social purpose. The analysis is based on the data and the results are only for educational purposes._

### 1. Scraping the data

The morning conferences transcripts was scraped from the official website of the Mexican President. The code is available in the `amlo_scraper` folder. I used the `requests` and `beautifulsoup` libraries to scrape the data, and the entire code is available in the `scrape_amlo.py` file.

### 2. NLP Analysis

I implemented some cleaning and preprocessing techniques to the data; we removed several stopwords and used regular expressions to identify the president's utterances (I am not interested in utterances from the journalists or other people in the conferences).

Then, with a small dataset of 'aggressive sentences' we created a custom model using a neural network to predict the 'aggressivity' of the president's speeches.

All of the code is available in the `nlp_analyzer` folder. You will see the code for an XGBoost model and a neural network model, along with a `utils` folder with helper functions and scripts to preprocess the data.


### 3. Cross-reference with homicides data

I then scraped the data of the homicides in Mexico from the official website of the Mexican government. For each day, the official estimate was in a PDF file, so I first scraped those PDFs (see `murder_incidences_scraper` folder) and then extracted the data from the PDFs (see `process_pdfs` folder).


