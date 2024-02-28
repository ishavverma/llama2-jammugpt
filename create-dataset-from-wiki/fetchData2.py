import requests
from bs4 import BeautifulSoup
import openai
import csv
import time
import logging

# Set your OpenAI GPT API key
openai.api_key = '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'

# Configure logging
logging.basicConfig(filename='script_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_wikipedia_links(keyword, api_url):
    base_url = api_url
    
    # Define parameters for the API request
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': keyword,
        'utf8': 1
    }

    # Make the API request
    response = requests.get(base_url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract page names and links from the search results
        pages = [{'name': result['title'], 'link': f"{api_url}/wiki/{result['title']}"}
                 for result in data['query']['search']]

        return pages
    else:
        logging.error(f"Error: Unable to fetch Wikipedia search results from {api_url}. Status code: {response.status_code}")
        return []

def search_in_multiple_apis(keyword):
    # List of Wikipedia API URLs
    wikipedia_apis = [
        "https://en.wikipedia.org/w/api.php",
        "https://es.wikipedia.org/w/api.php"  # Example for the Spanish Wikipedia
        # Add more API URLs if needed
    ]

    all_pages = []
    for api_url in wikipedia_apis:
        search_results = get_wikipedia_links(keyword, api_url)
        if search_results:
            all_pages.extend(search_results)

    return all_pages

def extract_page_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        page_soup = BeautifulSoup(response.text, 'html.parser')
        content = page_soup.find('div', {'class': 'mw-parser-output'})
        if content:
            # Extract text from paragraphs
            paragraphs = content.find_all('p')
            text_content = '\n'.join([paragraph.get_text() for paragraph in paragraphs])
            return text_content
        else:
            logging.warning(f"Warning: No content found on the Wikipedia page.")
            return None
    else:
        logging.error(f"Error: Unable to fetch Wikipedia page. Status code: {response.status_code}")
        return None

def generate_summary(text):
    # Use OpenAI GPT to generate a summary
    prompt = f"Summarize the following text:\n{text}"
    
    while True:
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150
            )
            summary = response['choices'][0]['text'].strip()
            return summary
        except openai.error.RateLimitError as e:
            # Handle rate limit error by waiting for 30 seconds and then retrying
            print("Rate limit exceeded. Waiting for 30 seconds and then retrying...")
            time.sleep(30)
        except Exception as e:
            logging.error(f"Error while generating summary: {e}")
            return None

def append_to_csv(data, csv_file_path):
    with open(csv_file_path, mode='a', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['Name', 'Link', 'Text', 'Summary']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Check if the file is empty, and write header if needed
        if csv_file.tell() == 0:
            writer.writeheader()

        for page in data:
            text = extract_page_text(page['link'])
            summary = generate_summary(text)
            writer.writerow({'Name': page['name'], 'Link': page['link'], 'Text': text, 'Summary': summary})
            print(f"Appended to CSV: {page['name']}")

if __name__ == "__main__":
    keyword = "Jammu"
    search_results = search_in_multiple_apis(keyword)

    if search_results:
        csv_file_path = "wikipedia_data.csv"
        append_to_csv(search_results, csv_file_path)
    else:
        logging.warning("No relevant Wikipedia pages found.")
