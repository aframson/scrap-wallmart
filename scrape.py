#!/usr/bin/env python3
"""
A simple script to fetch the product name and price from a Walmart product page,
then update a JSON file with the fetched data.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import argparse


def fetch_product_info(url):
    """
    Fetches product title and price from a given Walmart product page URL.
    Returns a dict: {"url": url, "name": ..., "price": ...}
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/90.0.4430.85 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Try to find product name
    title_elem = soup.find('h1', class_='prod-ProductTitle') or soup.find('h1', id='product-title')
    name = title_elem.get_text(strip=True) if title_elem else None

    # Try to find price
    price = None
    # First approach: itemprop="price"
    price_elem = soup.find(itemprop='price')
    if price_elem and price_elem.get('content'):
        price = price_elem['content']
    else:
        # Second approach: split whole & mantissa
        whole = soup.find('span', class_='price-characteristic')
        mantissa = soup.find('span', class_='price-mantissa')
        if whole and whole.get('content'):
            price = whole['content']
            if mantissa and mantissa.get('content'):
                price += f'.{mantissa["content"]}'

    return {"url": url, "name": name, "price": price}


def update_json_record(record, filepath):
    """
    Loads existing file (list of records) or initializes a new list,
    appends the new record, and writes back to filepath.
    """
    data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = []

    data.append(record)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Fetch Walmart product info and update a JSON file.')
    parser.add_argument('url', help='URL of the Walmart product page to scrape')
    parser.add_argument('-o', '--output', default='data.json',
                        help='Path to the JSON file to update (default: data.json)')
    args = parser.parse_args()

    info = fetch_product_info(args.url)
    update_json_record(info, args.output)
    print(f"Updated '{args.output}' with:\n  Name: {info['name']}\n  Price: {info['price']}")


if __name__ == '__main__':
    main()
