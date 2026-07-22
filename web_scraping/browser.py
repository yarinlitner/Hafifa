import os, json, base64

import requests, bs4
from playwright.sync_api import sync_playwright

with open("urls.input") as file:
    lines = [line.rstrip() for line in file]

try:
    os.mkdir('output')
except:
    pass

for url_number in range(len(lines)):
    try:
        os.mkdir(f'output/url_{url_number}')
    except:
        pass

    with open(f'output/url_{url_number}/browse.json', 'w') as outfile:
        output_dict = {}
        response = requests.get(lines[url_number])
        response.raise_for_status()
        output_dict.update({"html": response.text})

        soup = bs4.BeautifulSoup(response.text, features='html.parser')
        urls_found = [elem.attrs.get("href") for elem in soup.select("a")]
        output_dict.update({"resources": urls_found})

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            context.set_default_timeout(10000)
            page = context.new_page()
            page.goto(lines[url_number])
            screenshot_bytes = page.screenshot()
            encoded_string = base64.b64encode(screenshot_bytes).decode()
            output_dict.update({"screenshot": encoded_string})
            context.close()
            browser.close()

        json.dump(output_dict, outfile)
