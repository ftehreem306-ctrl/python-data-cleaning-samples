Web Scraping Basics: How to Pull Data From a Website With Python

If you've ever wished you could pull structured data from a website into a spreadsheet without copying and pasting it by hand, web scraping is the tool for the job. In this tutorial, you'll write a small Python script that requests a web page, finds the data you care about inside the page's HTML, and saves it to a CSV file you can open in Excel or load into pandas.

By the end, you'll understand:

- How a web page's HTML structure maps to the data you want to extract
- How to send an HTTP request and parse the response with `requests` and `BeautifulSoup`
- How to loop through multiple pages of results
- What separates responsible scraping from the kind that gets your IP blocked

Setting Up

You'll need two libraries: `requests`, which fetches the raw HTML of a page, and `beautifulsoup4`, which parses that HTML so you can search it like a tree instead of a wall of text.

```bash
pip install requests beautifulsoup4
```

For this tutorial, you'll scrape [quotes.toscrape.com](http://quotes.toscrape.com), a site built specifically for practicing scraping. Using a sandbox site like this one means you can learn the mechanics without worrying about a site's terms of service.

Step 1: Fetch the Page

Start by requesting the page and checking that it loaded successfully:

```python
import requests

url = "http://quotes.toscrape.com"
response = requests.get(url)

print(response.status_code)  # 200 means success
```

A status code of `200` means the server sent back the page as expected. If you see `403` or `404`, the page either blocked the request or doesn't exist at that URL — that's your first debugging checkpoint before you write another line of code.

Step 2: Inspect the HTML Structure

Before you can extract anything, you need to know where it lives in the page. Open the page in your browser, right-click a quote, and select "Inspect." You'll see something like this:

```html
<div class="quote">
    <span class="text">"The world as we have created it is a process of our thinking..."</span>
    <span>
        by <small class="author">Albert Einstein</small>
    </span>
</div>
```

Each quote lives inside a `<div class="quote">`, with the quote text in a `<span class="text">` and the author's name in a `<small class="author">`. This pattern — inspect first, code second — will save you far more time than guessing at selectors.

Step 3: Parse the HTML With BeautifulSoup

Now turn that raw HTML into something Python can search:

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")

quotes = soup.find_all("div", class_="quote")
print(f"Found {len(quotes)} quotes on this page")
```

`find_all()` returns every element matching your criteria — in this case, every `<div>` with the class `quote`. Each item in `quotes` is itself a small chunk of HTML you can dig further into.

Step 4: Extract the Data You Want

Loop through each quote block and pull out the text and author:

```python
data = []

for quote in quotes:
    text = quote.find("span", class_="text").get_text(strip=True)
    author = quote.find("small", class_="author").get_text(strip=True)
    data.append({"quote": text, "author": author})

for item in data[:3]:
    print(item)
```

`get_text(strip=True)` pulls just the visible text out of a tag and trims extra whitespace — without it, you'd get a lot of stray line breaks and indentation baked into your data.

Step 5: Handle Multiple Pages

Most real scraping targets spread data across several pages. `quotes.toscrape.com` uses a predictable URL pattern (`/page/1/`, `/page/2/`, and so on), so you can loop through pages until there are no more "Next" buttons:

```python
import time

all_quotes = []
page = 1

while True:
    response = requests.get(f"http://quotes.toscrape.com/page/{page}/")
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = soup.find_all("div", class_="quote")

    if not quotes:
        break

    for quote in quotes:
        text = quote.find("span", class_="text").get_text(strip=True)
        author = quote.find("small", class_="author").get_text(strip=True)
        all_quotes.append({"quote": text, "author": author})

    page += 1
    time.sleep(1)  # be polite — don't hammer the server

print(f"Scraped {len(all_quotes)} quotes total")
```

Notice the `time.sleep(1)` call. It costs you almost nothing in speed, and it's the difference between a script that behaves like a normal visitor and one that looks like an attack.

Step 6: Save the Results

Finally, write everything to a CSV so it's usable outside your script:

```python
import csv

with open("quotes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["quote", "author"])
    writer.writeheader()
    writer.writerows(all_quotes)
```

Open `quotes.csv` and you'll have a clean, structured file — the same kind of output you'd get from scraping product prices, job listings, or research citations.

A Note on Scraping Responsibly

Before you point this same script at a real website, check two things:

1. **The site's `robots.txt` file** (e.g., `example.com/robots.txt`) tells you which pages the site owner doesn't want automated tools to access.
2. **The site's terms of service** may prohibit scraping outright, regardless of what `robots.txt` says.

When in doubt, look for an official API first — it's usually more stable and more welcome than scraping the HTML directly.

## Where to Go From Here

This script covers the core loop behind almost every scraping project: fetch, parse, extract, repeat. From here, you could:

- Swap `requests` for `httpx` to make asynchronous requests and scrape multiple pages concurrently
- Use `selenium` or `playwright` for sites that load content with JavaScript, which `requests` can't see
- Schedule the script to run daily and track how the data changes over time

The mechanics stay the same; only the selectors and the target change.

