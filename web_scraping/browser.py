import os, sys, json, base64
from abc import ABC, abstractmethod
from typing import TypedDict, List, Protocol

import requests, bs4
from playwright.sync_api import sync_playwright

class WebsiteMetadata(TypedDict):
    html: str
    resources: List[str]
    screenshot: str

class UrlProvider(Protocol):
    def get_urls(self) -> list[str]:
        pass

class UrlFromFileProvider(UrlProvider):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def get_urls(self) -> list[str]:
        with open(self.filepath, "r") as file:
            return [url.rstrip() for url in file if url.strip()]

class HTMLParser(Protocol):
    def extract_links(self, html_content: str) -> list[str]:
        pass
        
class Bs4HtmlParser(HTMLParser):
    def extract_links(self, html_content: str) -> list[str]:
        soup = bs4.BeautifulSoup(html_content, features='html.parser')
        links_found = [
            elem.attrs.get("href") 
            for elem in soup.select("a") 
            if elem.attrs.get("href")
        ]

        return links_found

class HTMLFetcher(Protocol):
    def fetch(self, url: str) -> str:
        pass

class RequestsFetcher(HTMLFetcher):
    def fetch(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()

        return response.text
    
class MetadataWriter(Protocol):
    def write(self, metadata: WebsiteMetadata, filename: str) -> None:
        pass

class JsonMetadataWriter:
    def __init__(self, directory_path: str):
        self.directory_path = directory_path

        os.makedirs(self.directory_path, exist_ok=True)
    
    def write(self, metadata: WebsiteMetadata, filename: str) -> None:
        with open(f'{self.directory_path}/{filename}', 'w') as outfile:
            json.dump(metadata, outfile, indent=2)

class ScreenshotService(Protocol):
    def encoded_screenshot(self, url: str):
        pass

class PlaywrightScreenshotService():
    def __init__(self, timeout_ms: int = 10000):
        self.timeout_ms = timeout_ms

        self._playwright = None
        self._browser = None
        self._context = None
    
    def __enter__(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch()
        self._context = self._browser.new_context()
        self._context.set_default_timeout(self.timeout_ms)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def encoded_screenshot(self, url: str):
        result: str = ""        
        page = self._context.new_page()

        try:
            page.goto(url)
            screenshot_bytes = page.screenshot()
            result = base64.b64encode(screenshot_bytes).decode()
        except Exception as e:
            print("Error generating screenshot: ", e)
        finally:
            page.close()

        return result

class MetadataScraperPipeline:
    def __init__(
            self,
            parser: HTMLParser,
            fetcher: HTMLFetcher,
            screenshoter: ScreenshotService,
            writer: MetadataWriter):
        self.parser = parser
        self.fetcher = fetcher
        self.screenshoter = screenshoter
        self.writer = writer

    def run(self, url: str, url_number: int) -> None:
        html = self.fetcher.fetch(url)
        resources = self.parser.extract_links(html)
        screenshot = self.screenshoter.encoded_screenshot(url)

        metadata: WebsiteMetadata = {
            "html": html,
            "resources": resources,
            "screenshot": screenshot
        }

        self.writer.write(metadata, f'url_{url_number}')

if __name__ == "__main__":
    provider = UrlFromFileProvider("urls.input")
    parser = Bs4HtmlParser()
    fetcher = RequestsFetcher()
    writer = JsonMetadataWriter("output")

    with PlaywrightScreenshotService() as screenshotter:
        pipeline = MetadataScraperPipeline(
            parser=parser,
            fetcher=fetcher,
            screenshoter=screenshotter,
            writer=writer
        )

        for url_number, url in enumerate(provider.get_urls(), start=1):
            pipeline.run(url=url, url_number=url_number)