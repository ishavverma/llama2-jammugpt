import os
import requests
from bs4 import BeautifulSoup
import openai
import time

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
            print(f"Warning: No content found on the Wikipedia page.")
            return None
    else:
        print(f"Error: Unable to fetch Wikipedia page. Status code: {response.status_code}")
        return None

def generate_summary(text):
    # Use OpenAI GPT to generate a summary
    prompt = f"Summarize the following text:\n{text}"
    
    while True:
        try:
            response = openai.Completion.create(
                engine="davinci-002",
                prompt=prompt,
                max_tokens=150
            )
            summary = response['choices'][0]['text'].strip()
            return summary
        except openai.error.RateLimitError as e:
            # Handle rate limit error by waiting and then retrying
            wait_time = int(e.response.headers['Retry-After'])
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds and then retrying...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error while generating summary: {e}")
            return None

text_file_path = 'wikipedia_data.txt'
def save_to_text_file(data, text_file_path):
    for page in data:
        text = extract_page_text(page['link'])
        if text:
            summary = generate_summary(text)
            if summary:
                print(f"Name: {page['name']}")
                print(f"Link: {page['link']}")
                print(f"Text: {text}")
                print(f"Summary: {summary}\n")
            else:
                print(f"Skipping due to summary generation error: {page['name']}")
        else:
            print(f"Skipping due to text extraction error: {page['name']}")

if __name__ == "__main__":
    keyword = "Jammu"
    search_results = get_wikipedia_links(keyword)

    if search_results:
        save_to_text_file(search_results, text_file_path)
    else:
        print("No relevant Wikipedia pages found.")
