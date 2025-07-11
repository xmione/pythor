# research.py

from crawler import crawl_and_save

# --- Start crawling ---
sources = [
    "https://realpython.com/python-web-scraping-practical-introduction/",
    "https://www.geeksforgeeks.org/python-programming-language/"
]

for domain, urls in sources.items():
    crawl_and_save(urls, output_file="python_articles.jsonl", max_pages=5, allowed_domain=domain)
