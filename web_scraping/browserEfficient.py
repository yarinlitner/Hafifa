import asyncio
import base64
import json
import os
from typing import List, Protocol, TypedDict

import aiofiles
import bs4
import httpx
from playwright.async_api import async_playwright

class WebsiteMetadata(TypedDict):
    html: str
    resources: List[str]
    screenshot: str

class UrlProvider(Protocol):
    async def get_urls(self) -> list[str]:
        pass

class UrlFromFileProvider(UrlProvider):
    def __init__(self, filepath: str):
        self.filepath = filepath

    async def get_urls(self) -> list[str]:
        async with aiofiles.open(self.filepath, "r") as file:
            lines = await file.readlines()

            return [url.rstrip() for url in lines if url.strip()]

class HTMLParser(Protocol):
    async def extract_links(self, html_content: str) -> list[str]:
        pass

class Bs4HtmlParser(HTMLParser):
    async def extract_links(self, html_content: str) -> list[str]:
        soup = bs4.BeautifulSoup(html_content, features="html.parser")
        links_found = [
            elem.attrs.get("href")
            for elem in soup.select("a")
            if elem.attrs.get("href")
        ]
        return links_found

class HTMLFetcher(Protocol):
    async def fetch(self, url: str) -> str:
        pass


class HttpxFetcher(HTMLFetcher):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def fetch(self, url: str) -> str:
        response = await self.client.get(url)
        response.raise_for_status()
        return response.text

class MetadataWriter(Protocol):
    async def write(self, metadata: WebsiteMetadata, filename: str) -> None:
        pass

class JsonMetadataWriter(MetadataWriter):
    def __init__(self, directory_path: str):
        self.directory_path = directory_path
        os.makedirs(self.directory_path, exist_ok=True)

    async def write(self, metadata: WebsiteMetadata, filename: str) -> None:
        filepath = os.path.join(self.directory_path, filename)
        async with aiofiles.open(filepath, "w") as outfile:
            await outfile.write(json.dumps(metadata, indent=2))

class ScreenshotService(Protocol):
    async def encoded_screenshot(self, url: str) -> str:
        pass

class PlaywrightScreenshotService(ScreenshotService):
    def __init__(self, timeout_ms: int = 10000):
        self.timeout_ms = timeout_ms
        self._playwright = None
        self._browser = None
        self._context = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch()
        self._context = await self._browser.new_context()
        self._context.set_default_timeout(self.timeout_ms)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def encoded_screenshot(self, url: str) -> str:
        result: str = ""
        page = await self._context.new_page()

        try:
            await page.goto(url)
            screenshot_bytes = await page.screenshot()
            return base64.b64encode(screenshot_bytes).decode()
        except Exception as e:
            print("Error generating screenshot:", e)
            return ""
        finally:
            await page.close()

class MetadataScraperPipeline:
    def __init__(
        self,
        parser: HTMLParser,
        fetcher: HTMLFetcher,
        screenshoter: ScreenshotService,
        writer: MetadataWriter,
    ):
        self.parser = parser
        self.fetcher = fetcher
        self.screenshoter = screenshoter
        self.writer = writer

    async def run(self, url: str, url_number: int) -> None:
        html_task = asyncio.create_task(self.fetcher.fetch(url))
        screenshot_task = asyncio.create_task(
            self.screenshoter.encoded_screenshot(url)
        )

        html, screenshot = await asyncio.gather(html_task, screenshot_task)
        resources = await self.parser.extract_links(html)

        metadata: WebsiteMetadata = {
            "html": html,
            "resources": resources,
            "screenshot": screenshot,
        }

        await self.writer.write(metadata, f"url_{url_number}.json")

async def main(provider: UrlProvider, parser: HTMLParser, writer: MetadataWriter):
    urls = await provider.get_urls()

    async with httpx.AsyncClient(follow_redirects=True) as httpx_client, PlaywrightScreenshotService() as screenshotter:
        fetcher = HttpxFetcher(client=httpx_client)
        pipeline = MetadataScraperPipeline(
            parser=parser,
            fetcher=fetcher,
            screenshoter=screenshotter,
            writer=writer,
        )

        tasks = [
            pipeline.run(url=url, url_number=url_number)
            for url_number, url in enumerate(urls, start=1)
        ]
        await asyncio.gather(*tasks)

        for url_number, url in enumerate(urls, start=1):
            await pipeline.run(url=url, url_number=url_number)

if __name__ == "__main__":
    provider = UrlFromFileProvider("urls.input")
    parser = Bs4HtmlParser()
    writer = JsonMetadataWriter("output")
    asyncio.run(main(provider, parser, writer))