import requests
from bs4 import BeautifulSoup

# Specify the URL you want to scrape
url = "https://www.luscious.net"

# Connect to the website and get the HTML
response = requests.get(url)

# If the request is successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find elements by HTML tags, attributes, etc.
    titles = soup.find_all('h1')  # Example: find all <h1> tags
    for title in titles:
        print(title.text)  # Print the text content of each <h1>
else:
    print("Failed to retrieve the webpage")
