# Finding Philosophy

From [Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy):

>Clicking on the first link in the main text of a Wikipedia article, and then repeating the process for subsequent articles, will usually lead to the Philosophy article.

This script starts on a random Wikipedia article and follows the first link in the main body of the article. This link must not be within parentheses, italicized, pointing to an external site outside Wikipedia, or ending in an error. It repeats this link-finding process until the Philosophy page is reached, or until it finds a never-ending loop or a page with no links in the main body.

In order to get some statistics on the path length (i.e. how many pages it takes to find philosophy), the script records the distance in pages from the initial random article to the Philosophy page. To expedite the searches, we also record the path lengths of _every_ page accessed. During each run, before proceeding to find the next link, the script checks against this record of all pages to make sure the page has not been visited before. If it has, we can stop the search there and use the recorded number.

To make sure it doesn't get caught in an infinite loop, we also record every page visited in a particular run, ending the search if we land on an article that has already been visited.

---

Running `$ python find_philosophy.py` will start a search from 500 random wikipedia articles, printing out pages as they are accessed as well as the final outcome of the searches.

Once the 500 searches are done, data on distribution of path lengths is also displayed.

__For overview of distribution, please see ipython notebook [`find_philosophy.ipynb`](find_philosophy.ipynb) .__

---

### Requirements:

python==3.6.1
- pandas==0.19.2
- requests==2.13.0
- beautifulsoup4==4.5.3
