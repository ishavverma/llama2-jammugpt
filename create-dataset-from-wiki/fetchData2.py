import openai
import requests
from bs4 import BeautifulSoup
import csv

# Set your OpenAI GPT API key
openai.api_key = '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'

def get_wikipedia_links(keyword):
    base_url = "https://en.wikipedia.org/w/api.php"
    
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
        pages = [{'name': result['title'], 'link': f"https://en.wikipedia.org/wiki/{result['title']}"}
                 for result in data['query']['search']]

        return pages
    else:
        print(f"Error: Unable to fetch Wikipedia search results. Status code: {response.status_code}")
        return []

def generate_summary(text):
    # Use OpenAI GPT to generate a summary
    prompt = f"Summarize the following text:\n{text}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )

    summary = response['choices'][0]['text'].strip()
    return summary

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
            print(f"Error: No content found on the Wikipedia page.")
            return None
    else:
        print(f"Error: Unable to fetch Wikipedia page. Status code: {response.status_code}")
        return None

if __name__ == "__main__":
    keyword = "Jammu"
    search_results = get_wikipedia_links(keyword)

    if search_results:
        csv_file_path = "wikipedia_data.csv"
        append_to_csv(search_results, csv_file_path)
    else:
        print("No relevant Wikipedia pages found.")
