import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


output_dir = "output"


visited_urls = set()


def create_output_dir():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def save_file(url, content, extension=None):
    parsed_url = urlparse(url)
    path = parsed_url.path
    if not path:
        path = 'index.html'
    filename = os.path.join(output_dir, os.path.basename(path))
    if extension and not filename.endswith(extension):
        filename += extension
    with open(filename, 'wb') as f:
        f.write(content)


def grab_webserver(url, base_url=None):
    if url in visited_urls:
        return
    visited_urls.add(url)

    try:
        response = requests.get(url)
        response.raise_for_status()


        parsed_url = urlparse(url)
        path = parsed_url.path
        if not path:
            path = 'index.html'
        extension = os.path.splitext(path)[1]
        if not extension:
            extension = '.html'  # Default to .html if no extension is found


        save_file(url, response.content, extension)

        # If the file is HTML, parse it to find and save linked files
        if extension == '.html':
            soup = BeautifulSoup(response.content, 'html.parser')


            for link in soup.find_all(['a', 'link', 'script', 'img']):
                if link.name == 'a':
                    href = link.get('href')
                    if href:
                        absolute_url = urljoin(url, href)
                        if absolute_url not in visited_urls:
                            grab_webserver(absolute_url, base_url)
                elif link.name == 'link':
                    href = link.get('href')
                    if href and 'stylesheet' in link.get('rel', []):
                        absolute_url = urljoin(url, href)
                        if absolute_url not in visited_urls:
                            grab_webserver(absolute_url, base_url)
                elif link.name == 'script':
                    src = link.get('src')
                    if src:
                        absolute_url = urljoin(url, src)
                        if absolute_url not in visited_urls:
                            grab_webserver(absolute_url, base_url)
                elif link.name == 'img':
                    src = link.get('src')
                    if src:
                        absolute_url = urljoin(url, src)
                        if absolute_url not in visited_urls:
                            grab_webserver(absolute_url, base_url)

    except requests.exceptions.RequestException as e:
        print(f"Failed to grab {url}: {e}")

# Main function
def main():
    create_output_dir()
    base_url = input("Enter the URL of the webserver to grab: ")
    grab_webserver(base_url, base_url)
    print("Webserver grabbing completed. Files saved in the 'output' directory.")

if __name__ == "__main__":
    main()