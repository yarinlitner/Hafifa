import os, json, base64
from abc import ABC, abstractmethod
from typing import TypedDict, List

import requests, bs4
from playwright.sync_api import sync_playwright

class WebsiteMetadata(TypedDict):
    html: str
    resources: List[str]
    screenshot: str

class UrlProvider(ABC):
    @abstractmethod
    def get_urls(self) -> list[str]:
        pass

class UrlFromFileProvider(UrlProvider):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def get_urls(self) -> list[str]:
        with open(self.filepath, "r") as file:
            return [url.rstrip() for url in file if url.strip()]

class HTMLParser(ABC):
    @abstractmethod
    def extract_links(self, html_content: str) -> list[str]:
        pass
        
class Bs4HtmlParser(HTMLParser):
    def extract_links(self, html_content: str) -> list[str]:
        soup = bs4.BeautifulSoup(html_content, features='html.parser')
        return [
            elem.attrs.get("href") 
            for elem in soup.select("a") 
            if elem.attrs.get("href")
        ]

def get_encoded_screenshot(url: str):
    result: str = ""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        context.set_default_timeout(10000)
        page = context.new_page()
        page.goto(url)
        screenshot_bytes = page.screenshot()
        result = base64.b64encode(screenshot_bytes).decode()
        context.close()
        browser.close()
    return result

def main():
    provider = UrlFromFileProvider("urls.input")
    parser = Bs4HtmlParser()

    urls = provider.get_urls()

    try:
        os.mkdir('output')
    except FileExistsError as e:
        print(e)
        pass

    for url_number, url in enumerate(urls, start=1):
        try:
            os.mkdir(f'output/url_{url_number}')
        except FileExistsError as e:
            print(e)
            pass

        response = requests.get(url)
        response.raise_for_status()
        html_string = response.text

        urls_found = parser.extract_links(html_string)

        encoded_screenshot = get_encoded_screenshot(url)

        website_metadata: WebsiteMetadata = {
            "html": html_string,
            "resources": urls_found,
            "screenshot": encoded_screenshot
        }

        with open(f'output/url_{url_number}/browse.json', 'w') as outfile:
            json.dump(website_metadata, outfile)

if __name__ == "__main__":
    main()