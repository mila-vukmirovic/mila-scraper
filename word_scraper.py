""" Scrape a website and return a dictionary of most used words """

import re as _re

import requests as _requests
import bs4 as _bs4


BLACKLISTED_ELEMENTS = [
    '[document]',
    'noscript',
    'header',
    'html',
    'meta',
    'head',
    'input',
    'script',
    # there may be more elements you don't want, such as "style", etc.
]

BLACKLISTED_WORDS = [
    'class', 'div', 'label', 'fieldset', 'banner', 'popup'
]


def _scrape_website(url: str) -> list:
    """
    Scrape a website with the following workflow:
        1) Get response for an HTTP request
        2) Extract text from HTML content
        3) Split the text into words
        4) Iterate over words, and store the words into a dictionary
            {<word>: <number of occurrences>}.
        5) Convert the dictionary into a list of pairs
            (<word>, <number of occurrences>),
            sorted by number of occurrences descending.
    """
    response = _requests.get(url)
    if not response.ok:
        raise RuntimeError(f"Failed HTTP request, status code: {response.status_code}")

    soup = _bs4.BeautifulSoup(response.content, 'html.parser')
    text = soup.find_all(text=True)

    words = {}  # initialize empty words dictionary
    for segment in text:  # iterate over segments
        if segment.parent.name not in BLACKLISTED_ELEMENTS:  # ignore random html garbage
            for word in _re.split(r'\W', segment.lower()):  # split into words
                if word and word not in BLACKLISTED_WORDS:  # ignore likely html words
                    words[word] = 1 if word not in words else words[word] + 1

    # This is a fancy one-line sorting expression, it could be done in a more
    # readable way, but this is shorter :)
    sorted_words = [(k, words[k]) for k in
                    sorted(words.keys(), key=lambda k: words[k], reverse=True)]

    return sorted_words


if __name__ == '__main__':
    # url = "https://www.lemo.com/en/products/low-voltage-connector"
    # url = "https://www.ebay.com/b/Lemo-Connectors/bn_7024950655"
    url = "https://www.peigenesis.com/en/lemo/lemo-l-series-connector.html"
    sorted_words = _scrape_website(url)
    print("\n".join((f"{word}: {count}" for word, count in sorted_words[:20])))
