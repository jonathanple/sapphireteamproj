import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Config
BASE_URL = "https://www.valleywater.org"
START_PAGE = "https://www.valleywater.org/careers-job-openings"
ALLOWED_DOMAIN = "valleywater.org"

visited = set()
scraped_pages = {}

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.netloc == ALLOWED_DOMAIN or parsed.netloc == ""

def crawl(url, depth=1):
    if url in visited or depth == 0:
        return
    print(f"Scraping: {url}")
    visited.add(url)

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        scraped_pages[url] = text

        for link_tag in soup.find_all("a", href=True):
            full_url = urljoin(url, link_tag['href'])
            if is_valid_url(full_url) and BASE_URL in full_url:
                crawl(full_url, depth=depth-1)

    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

# Start crawling
if __name__ == "__main__":
    crawl(START_PAGE, depth=2)  # Set depth=2 to explore links within the main page
    # Save the content to a file
output_path = "insert output path here"

with open(output_path, "w", encoding="utf-8") as f:
    for url, content in scraped_pages.items():
        f.write(f"URL: {url}\n{content}\n\n{'='*80}\n\n")

    print(f"Scraped {len(scraped_pages)} pages.")


    
