""" Scrape a website and return a dictionary of most used words """

import re as _re
import time as _time

import bs4 as _bs4
import requests as _requests
#import xlsxwriter
# import numpy as np
import pandas
import xlwt
from xlwt import Workbook


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
    'class', 'div', 'label', 'fieldset', 'banner', 'popup', 'and', 'our', 'we', 'is', 'to', 'about','in',
    'the','at','a','of','s','on','can','for','from','that','how','with','why','out','as','must','are','gmbh','co',
    'if','ie','endif','gte','jquery','en','script','fr','has','this','more','9','you','us','all','end','noscript',
    'set','log','be','de','javascript'
]

TIMEOUT_IN_SECONDS = 10
MAX_WORD_LENGTH = 50  # how many characters can one word be long at most


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
    t0 = _time.time()
    try:
        response = _requests.get(url, timeout=TIMEOUT_IN_SECONDS)
    except Exception as e:
        print(f"Failed HTTP request, reason: {e}")
        return []

    if not response.ok:
        print(f"Failed HTTP request, status code: {response.status_code}")
        return []

    soup = _bs4.BeautifulSoup(response.content, 'html.parser')
    text = soup.find_all(text=True)

    words = {}  # initialize empty words dictionary
    for segment in text:  # iterate over segments
        if segment.parent.name not in BLACKLISTED_ELEMENTS:  # ignore random html garbage
            for word in _re.split(r'\W', segment.lower()):  # split into words
                if word and word not in BLACKLISTED_WORDS and len(word) <= MAX_WORD_LENGTH:  # ignore likely html words
                    words[word] = 1 if word not in words else words[word] + 1

    # This is a fancy one-line sorting expression, it could be done in a more readable way, but this is shorter :)
    sorted_words = [(k, words[k]) for k in
                    sorted(words.keys(), key=lambda k: words[k], reverse=True)]

    duration = _time.time() - t0
    print(f"Successfully crawled url: {url} in {duration:.2f} seconds.")
    return sorted_words


input_filename = 'Links2.xlsx'
df = pandas.read_excel(input_filename)

#with xlsxwriter.Workbook('test.xlsx') as workbook:
#    worksheet = workbook.add_worksheet()

 #   for row_num, data in enumerate(sorted_words):
  #      worksheet.write_row(row_num, 0, data)


# Workbook is created
wb = Workbook()
sheet1 = wb.add_sheet('Sheet 1')

# ovo nam treba da bi newline radio
style = xlwt.XFStyle()
style.alignment.wrap = 1

cnt = 0
for i, row in df.iterrows():
    url = row['SUBLINK']
    sorted_words = _scrape_website(url)
    words_str = "\n".join((f"{word}: {count}" for word, count in sorted_words))  # napravi string od liste
    sheet1.write(i, 0, url)
    sheet1.write(i, 1, words_str, style)
    cnt += 1


wb.save('final.xls')

# below exportation to a txt file
#with open('test.txt', 'w+') as datafile_id:
#here you open the ascii file
#    np.savetxt(datafile_id, sorted_words, fmt=['%s','%s'])