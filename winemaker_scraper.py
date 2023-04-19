import requests
from bs4 import BeautifulSoup
import pandas as pd
from googletrans import Translator

# Initialize
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

# Helper functions
def load_existing_data(filename):
    """Load existing data from the CSV file or create an empty DataFrame."""
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["URL", "Winemaker", "Information"])
    return df

def fetch_sitemap(sitemap_url, headers):
    """Fetch the sitemap XML."""
    response = requests.get(sitemap_url, headers=headers)
    content = response.content
    return BeautifulSoup(content, "xml")

def get_filtered_urls(sitemap_soup, exclusions):
    """Filter out the unwanted URLs."""
    url_elements = sitemap_soup.find_all("url")
    filtered_urls = [
        (url.find("loc").text, url.find("image:title").text)
        for url in url_elements
        if url.find("loc") and url.find("image:title") and not any(x in url.find("loc").text for x in exclusions)
    ]
    return filtered_urls

def fetch_profile(url, headers):
    """Fetch the profile content."""
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, "html.parser")

def extract_information(profile_soup):
    """Extract information from the profile content."""
    info_text = " ".join(
        p.text.strip()
        for block in profile_soup.find_all("div", class_="sqs-block-content")
        for p in block.find_all("p")
        if not p.text.strip() == "\xa0"
    )
    return info_text

# Main function
def main():
    existing_df = load_existing_data(csv_filename)
    sitemap_soup = fetch_sitemap("https://www.terrovin.be/sitemap.xml", headers)
    filtered_urls = get_filtered_urls(sitemap_soup, exclusions)

    for loc, image_title in filtered_urls:
        if not any(existing_df["URL"].str.contains(loc)):
            #time.sleep(3) # This can be helpful if the website blocks content

            print(f"Retrieved profile for {image_title} at {loc}")  # Add the print statement here
            profile_soup = fetch_profile(loc, headers)
            info_text = extract_information(profile_soup)
            
            translated_text = translator.translate(info_text, src="nl", dest="en").text # Choose your source and destination languages
            print(f"Translating {image_title} profile...")
            print()

            new_row = {"URL": loc, "Winemaker": image_title, "Translated Information": translated_text, "Information": info_text}
            existing_df = pd.concat([existing_df, pd.DataFrame(new_row, index=[0])], ignore_index=True)

    # Save the updated DataFrame to the CSV file
    existing_df = existing_df[["URL", "Winemaker", "Translated Information", "Information"]]
    existing_df.to_csv(csv_filename, index=False)

# Execution
if __name__ == "__main__":
    main()
