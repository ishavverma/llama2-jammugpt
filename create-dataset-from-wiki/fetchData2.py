import requests
import csv

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

def append_to_csv(data, csv_file_path):
    with open(csv_file_path, mode='a', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['Name', 'Link']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Check if the file is empty, and write header if needed
        if csv_file.tell() == 0:
            writer.writeheader()

        for page in data:
            writer.writerow({'Name': page['name'], 'Link': page['link']})
            print(f"Appended to CSV: {page['name']}")

if __name__ == "__main__":
    keyword = "Jammu"
    search_results = get_wikipedia_links(keyword)

    if search_results:
        csv_file_path = "wikipedia_data.csv"
        append_to_csv(search_results, csv_file_path)
    else:
        print("No relevant Wikipedia pages found.")
