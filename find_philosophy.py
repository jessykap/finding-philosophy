# -*- coding: utf-8 -*-
"""
Start on random article on Wikipedia and follow the first link
on main body of article that is not within parentheses or italicized,
repeating for each subsequent article until finding Philosophy page.

Stores 500 starting pages and their path lengths to Philosophy.

Keeps tracks of all visited pages and their path lengths to Philosophy
(to reduce number of http requests).

Path length value is negative if Philosophy wasn't reached.
"""



from bs4 import BeautifulSoup
import requests
import re
import pandas as pd


def remove_paren(text):
    """
    Remove parentheses from string if they are outside of tags.

    Args:
        text (string): All text from article's main section

    Returns:
        no_paren (string)

    >>> remove_paren('This is (remove this) some text.')
    This is  some text.

    >>> remove_paren('Here is <a tag with (parentheses) that> should be left.')
    'Here is <a tag with (parentheses) that> should be left.'

    >>> remove_paren('Once more (without <this>) <but (with) this>.')
    'Once more  <but (with) this>.'
    """

    paren_depth = 0
    tag_depth = 0
    no_paren = ''
    for i in text:

        if paren_depth == 0:
            # Tracks tags outside of parentheses
            if i == '<':
                tag_depth += 1
            if i == '>':
                tag_depth -= 1

        if tag_depth == 0:
            # Tracks parentheses outside of tags
            if i == '(':
                paren_depth += 1
            if paren_depth == 0:
                no_paren += i
            if i == ')':
                paren_depth -= 1

        else:
            # Store characters inside remaining tags
            no_paren += i

    return no_paren


def valid_url(url):
    """
    Checks if url is valid and reformats if needed.

    Args:
        url (string)

    Returns:
        url (string): If url contains invalid pattern, returns 'invalid'.

            If url is valid, remove section anchor (if needed) and
            returns url formatted as: 'http://en.wikipedia.org/wiki/some_page'.

    >>> valid_url('https://en.wikipedia.org/w/index.php?title=Burt_P._Lynwood&action=edit&redlink=1')
    'invalid'

    >>> valid_url('/wiki/Help:IPA_for_English')
    'invalid'

    >>> valid_url('#cite_note-3')
    'invalid'

    >>> valid_url('/wiki/Acacia')
    'http://en.wikipedia.org/wiki/Acacia'

    >>> valid_url('/wiki/Land#Land_mass')
    'http://en.wikipedia.org/wiki/Land'

    >>> valid_url('https://en.wikipedia.org/wiki/Class_(biology)')
    http://en.wikipedia.org/wiki/Class_(biology)
    """

    invalid_patterns = ['#cite',
                        'wikt:',
                        'wiktionary',
                        'redlink=',
                        'File:',
                        'Help:',
                        'Special:',
                        'Category:',
                        'Template:',
                        'Portal:',
                        'Wikipedia:',
                        'File talk:',
                        'Help talk:',
                        'Special talk:',
                        'Category talk:',
                        'Template talk:',
                        'Portal talk:',
                        'Wikipedia talk:',
                        'wikimedia']


    for pattern in invalid_patterns:
        if pattern in url:
            return 'invalid'

    octothorpe = url.find('#')
    if octothorpe != -1:
        url = url[:octothorpe]
    if url.startswith('https') and (url.find('wiki') != -1):
        url = 'http' + url[5:]
        return url
    if url.startswith('/wiki/'):
        url = 'http://en.wikipedia.org' + url
        return url
    if url.find('wiki') != -1:
        return url
    else:
        return 'invalid' # page outside of wikipedia


def get_next_url(soup):
    """
    Finds next valid link in given page.

    Args:
        soup (bs4.BeautifulSoup): BeautifulSoup of entire page

    Returns:
        None if no valid urls found.

        valid_url(url) (string): Correctly formatted next link.
    """

    # remove all italicized content
    for tag in soup.select("i"):
        tag.decompose()

    text = remove_paren(str(soup.select('div#mw-content-text > p')))
    clean_soup = BeautifulSoup(text, "html.parser")
    potential_links = clean_soup.find_all('a')

    if potential_links is None:
        return None

    for link in potential_links:
        url = link.get('href')

        if valid_url(url) != 'invalid':
            return valid_url(url)

    return None


def get_page_title(soup):
    """Returns title (string) of given page."""

    page_title = soup.title.text
    end_of_title = page_title.find(' - Wikipedia')
    return page_title[:end_of_title]


def find_philo():
    """
    Starting on a random wikipedia page, finds Philosophy.

    Returns:
        int: Length of path, -1 if Philosophy not found (no valid links found,
            or search ended in a loop).

        this_series (list): List of all pages in order of encounter.
    """

    i = 0
    this_series = [] # pages encountered in this run
    page_title = ''
    url = 'http://en.wikipedia.org/w/index.php?title=Special:Random' #random url
    philo_url = 'http://en.wikipedia.org/wiki/Philosophy'

    r = requests.get(url)
    url = r.url

    while url != philo_url:
        if i > 0:
            r = requests.get(url)

        soup = BeautifulSoup(r.text, "html.parser")
        page_title = get_page_title(soup)
        if i == 0:
            print("--- Starting on: ", page_title, " ---")
        else:
            print(page_title)

        if page_title in this_series:
            print("Circular path, ending search.")
            return -1, this_series

        if page_title in all_pages.page.values:
            print("Page already visited, ending search.")
            page_idx = all_pages.loc[all_pages.page==page_title].index.tolist()[0]
            num = all_pages.get_value(page_idx, 'count')
            if num > 0:
                print("Philosophy found in ", int(i + num), " steps.")
                return i + num, this_series
            else:
                return -1, this_series
                ("Failed to find Philosophy.")

        this_series.append(page_title)
        url = get_next_url(soup)
        if url is None:
            print("No valid links found, ending search.")
            return -1, this_series
        i += 1

    print("Philosophy found in ", i, " steps.")
    return i, this_series




all_pages = pd.DataFrame(columns=['page', 'count']) # cache including all pages encountered
starting_pages = pd.DataFrame(columns=['page', 'count']) # starting pages and their path lengths
i = 0

for i in range(500):
    count, this_series = find_philo()
    starting_pages = starting_pages.append({"page": this_series[0], "count": count}, ignore_index=True)
    for page in this_series:
        all_pages = all_pages.append({"page": page, "count": count}, ignore_index=True)
        count -= 1

print("Search done!")

distribution_all = starting_pages['count']
dist_end_in_philo = starting_pages[starting_pages['count'] >= 0]['count']

print("-----------------------------------------")
print(len(dist_end_in_philo), "/500 pages found Philosophy.")
print("Path lengths mean: ", dist_end_in_philo.mean())
print("Standard deviation: ", dist_end_in_philo.std())
print("Maximum: ", dist_end_in_philo.max())
print("Minimum: ", dist_end_in_philo.min())
print("Top five path lengths:")
print("Length | Count",)
print(dist_end_in_philo.value_counts().head())

# Store values for further analysis
starting_pages.to_csv('save/starting_pages.csv')
all_pages.to_csv('save/all_pages.csv')
dist_end_in_philo.to_csv('save/dist_end_in_philo.csv')
