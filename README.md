# Scraping and translating winemaker profiles with Python

In this tutorial, you will create a Python script to scrape winemaker profiles from a website, translate the scraped text, then save the data to a CSV file. You will use the `requests`, `BeautifulSoup`, `pandas`, and `googletrans` libraries to achieve this.

## Prerequisites

Before starting, please ensure you have the following:

- Python and pip installed on your system (preferably Python 3.6 or later).
- A code editor or IDE of your choice.
- Basic knowledge of Python and web scraping.


### Install required libraries

To begin, we will install the necessary libraries for our script. Open your command-line interface and run the following commands:

```bash
pip install requests
pip install beautifulsoup4
pip install pandas
pip install googletrans==4.0.0-rc1
```

## Create the script

### Import required libraries

In your code editor, create a new Python file called `winemaker_scraper.py`. Start by importing the required libraries:

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
from googletrans import Translator
```

### Initialize variables and functions

Next, define some variables and functions needed for your script:

```python
translator = Translator()
exclusions = [
    "https://www.terrovin.be/bestellen",
    "https://www.terrovin.be/prijslijst",
    "https://www.terrovin.be/contact",
    "https://www.terrovin.be/events",
    "https://www.terrovin.be/intro",
]
csv_filename = "winemaker_profiles.csv"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
}
```

The `exclusions` variable contains a list of URLs that we want to ignore when scraping the website. The `csv_filename` variable is the name of the CSV file where we will save the scraped data. The `headers` variable contains a custom User-Agent header to be used in our requests.

### Define helper functions

Now, create some helper functions to break down your script into smaller, more manageable parts. Below are the functions you will create:

- `load_existing_data(filename)`: this loads existing data from the CSV file or creates an empty DataFrame if no CSV file exists.
- `fetch_sitemap(sitemap_url, headers)`: this fetches the sitemap XML to get a list of all live webpages.
- `get_filtered_urls(sitemap_soup, exclusions)`: this filters out the unwanted URLs (in your `exclusions` variable).
- `fetch_profile(url, headers)`: this fetch the profile content.
- `extract_information(profile_soup)`: this extracts information from the profile content.

Add the following code to your script to define these helper functions:

```python
def load_existing_data(filename):
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["URL", "Winemaker", "Information"])
    return df

def fetch_sitemap(sitemap_url, headers):
    response = requests.get(sitemap_url, headers=headers)
    content = response.content
    return BeautifulSoup(content, "xml")

def get_filtered_urls(sitemap_soup, exclusions):
    url_elements = sitemap_soup.find_all("url")
    filtered_urls = [
        (url.find("loc").text, url.find("image:title").text)
        for url in url_elements
        if url.find("loc") and url.find("image:title") and not any(x in url.find("loc").text for x in exclusions)
    ]
    return filtered_urls

def fetch_profile(url, headers):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, "html.parser")

def extract_information(profile_soup):
    info_text = " ".join(
        p.text.strip()
        for block in profile_soup.find_all("div", class_="sqs-block-content")
        for p in block.find_all("p")
        if not p.text.strip() == "\xa0"
    )
    return info_text
```

**Note:** the `extract_information` function is customized for a single website. You will likely need to edit this function if scraping other websites. 

### Define the main function

Now that you have your helper functions in place, create the main function to drive your script. In this function, also use `Translator` module/library to translate the extracted information. Add the following code to your file:

```python
def main():
    existing_df = load_existing_data(csv_filename)
    sitemap_soup = fetch_sitemap("https://www.terrovin.be/sitemap.xml", headers)
    filtered_urls = get_filtered_urls(sitemap_soup, exclusions)

    for loc, image_title in filtered_urls:
        if not any(existing_df["URL"].str.contains(loc)):
            profile_soup = fetch_profile(loc, headers)
            info_text = extract_information(profile_soup)
            translated_text = translator.translate(info_text, src="nl", dest="en").text # Choose your source and destination languages

            new_row = {"URL": loc, "Winemaker": image_title, "Translated Information": translated_text, "Information": info_text}
            existing_df = pd.concat([existing_df, pd.DataFrame(new_row, index=[0])], ignore_index=True)

    # Save the updated DataFrame to the CSV file
    existing_df = existing_df[["URL", "Winemaker", "Translated Information", "Information"]]
    existing_df.to_csv(csv_filename, index=False)
```

Note that the last line of the `for` loop uses pandas concat function (`pd.concat`). This ensures that if you run the script multiple times, profiles are appended to the csv instead of over writing the csv. One potential drawback here is if the webpage owner updates a profile, the script won't take in updated information. The primary benefit, however, is if the webpage owner removes a profile, your csv will contain its history.

### Execute the functions

Finally, add the following code at the end of the script to execute the `main()` function when you the script:

```python
if __name__ == "__main__":
    main()
```

## Use the script

To use the script, open your command-line interface, navigate to the directory where the `winemaker_scraper.py` file is located, and enter the following command:

```bash
python winemaker_scraper.py
```
The script will then scrape the winemaker profiles, translate the text, and save the data to a CSV file named `winemaker_profiles.csv`. While the script is running, you will see output similiar to the following:

```bash
Retrieved profile for Caveau de Bacchus at https://www.terrovin.be/caveaudebacchus
Translating Caveau de Bacchus profile...

Retrieved profile for Pignier at https://www.terrovin.be/pignier
Translating Pignier profile...
```

## Conclusion

In this tutorial, you've built a Python script to scrape winemaker profiles, translate the scraped text, and save the data to a CSV file. This script can be further modified and expanded to scrape other websites or save the data in different formats. The skills learned in this tutorial can also be applied to other web scraping projects.