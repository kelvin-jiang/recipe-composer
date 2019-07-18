from bs4 import BeautifulSoup
import logging
import re
import requests

logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', level=logging.INFO)

EPICURIOUS_URL = 'https://www.epicurious.com'
HREF_REGEX = re.compile(r'/recipes/.*')
OUTPUT_FP = 'data/recipe-links.txt'

recipe_links = set()

page_num = 1
while page_num > 0:
    url = EPICURIOUS_URL + '/search/?content=recipe&page=' + str(page_num)
    html = requests.get(url)
    logging.info('OPENED %s', url)
    soup = BeautifulSoup(html.content, 'html.parser')

    links = soup.find_all('a', attrs={'itemprop': 'url', 'href': HREF_REGEX})
    if len(links) == 0:
        logging.info('NO MORE RECIPES FOUND')
        break

    for item in links:
        href = EPICURIOUS_URL + item.get('href')
        recipe_links.add(href)
        logging.info('RETRIEVED %s', href)

    page_num += 1

with open(OUTPUT_FP, 'w') as f:
    for link in recipe_links:
        f.write(link + '\n')
