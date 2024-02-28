import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import csv

def get_wikipedia_links(keyword):
    # Prepare the Wikipedia search URL
    search_url = f"https://en.wikipedia.org/w/index.php?search={quote_plus(keyword)}"

    # Send a request to the Wikipedia search page
    response = requests.get(search_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the search page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract links to relevant Wikipedia pages
        links = soup.select('.mw-search-result-heading a')

        # Return a list of Wikipedia page URLs
        return [link['href'] for link in links]
    else:
        print(f"Error: Unable to fetch search results. Status code: {response.status_code}")
        return []

def download_and_save_to_csv(links):
    csv_file_path = "wikipedia_data.csv"

    with open(csv_file_path, mode='w', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['Title', 'Content']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for link in links:
            # Construct the full URL for each Wikipedia page
            full_url = f"https://en.wikipedia.org{link}"

            # Send a request to the Wikipedia page
            page_response = requests.get(full_url)

            # Check if the request was successful
            if page_response.status_code == 200:
                # Parse the HTML content of the Wikipedia page
                page_soup = BeautifulSoup(page_response.text, 'html.parser')

                # Extract the title of the Wikipedia page
                title = page_soup.find('h1', {'class': 'firstHeading'}).text

                # Extract the main content of the Wikipedia page
                content = page_soup.find('div', {'class': 'mw-parser-output'}).text

                # Write title and content to CSV file
                writer.writerow({'Title': title, 'Content': content})
                print(f"Downloaded and saved to CSV: {title}")
            else:
                print(f"Error: Unable to fetch Wikipedia page. Status code: {page_response.status_code}")

if __name__ == "__main__":
    keyword = input("Enter keyword: ")
    search_results = get_wikipedia_links(keyword)

    if search_results:
        download_and_save_to_csv(search_results)
    else:
        print("No relevant Wikipedia pages found.")

