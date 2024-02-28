import requests

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

        # Extract page titles from the search results
        titles = [result['title'] for result in data['query']['search']]

        return titles
    else:
        print(f"Error: Unable to fetch Wikipedia search results. Status code: {response.status_code}")
        return []

if __name__ == "__main__":
    keyword = "Jammu"
    search_results = get_wikipedia_links(keyword)

    if search_results:
        print("Wikipedia pages containing the keyword:")
        for title in search_results:
            print(title)
    else:
        print("No relevant Wikipedia pages found.")
