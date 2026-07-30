import json, base64
from abc import ABC, abstractmethod
from typing import TypedDict, List
from pathlib import Path

import bs4, httpx, asyncio
from playwright.async_api import async_playwright, BrowserContext

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

async def get_encoded_screenshot(context: BrowserContext, url: str) -> str:
    page = await context.new_page()
    try:
        await page.goto(url)
        screenshot_bytes = await page.screenshot()
        return base64.b64encode(screenshot_bytes).decode()
    finally:
        await page.close()

async def process_url(
        url_number: int,
        url: str,
        http_client: httpx.AsyncClient,
        browser_context: BrowserContext,
        parser: HTMLParser,
        output_dir: Path
) -> None:
    try:
        response = await http_client.get(url, timeout=10.0)
        response.raise_for_status()
        html_string = response.text

        urls_found = parser.extract_links(html_string)

        encoded_screenshot = await get_encoded_screenshot(browser_context, url)

        website_metadata: WebsiteMetadata = {
            "html": html_string,
            "resources": urls_found,
            "screenshot": encoded_screenshot
        }

        file_path = output_dir / f"url_{url_number}.txt"

        with open(file_path, "w", encoding="utf-8") as outfile:
            json.dump(website_metadata, outfile, indent=2)

    except Exception as e:
        print(f"Error processing {url}: {e}")

async def main():
    provider = UrlFromFileProvider("urls.input")
    parser = Bs4HtmlParser()
    urls = provider.get_urls()
    output_dir = Path("output")

    async with httpx.AsyncClient(follow_redirects=True) as http_client:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            context.set_default_timeout(10000)

            tasks = [
                process_url(index, url, http_client, context, parser, output_dir) for index, url in enumerate(urls, start=1)
            ]

            await asyncio.gather(*tasks)
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())