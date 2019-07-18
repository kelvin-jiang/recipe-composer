from bs4 import BeautifulSoup
import json
import logging
from multiprocessing import Pool
import requests
from unidecode import unidecode

logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', level=logging.INFO)

RECIPE_LINKS_FP = 'data/recipe-links.txt'
OUTPUT_FP = '../recipes.json'

def get_recipe(url):
    recipe = {}
    try:
        html = requests.get(url)
        logging.info('OPENED %s', url)
        soup = BeautifulSoup(html.content, 'html.parser')

        # remove annoying suffix that comes with title
        name = soup.find('title').string.replace(' recipe | Epicurious.com', '')
        recipe['name'] = unidecode(name.strip())

        recipe['url'] = url

        rating = soup.find('span', class_='rating').string
        if rating:
            recipe['rating'] = unidecode(rating.strip())

        n_ratings = soup.find('span', class_='reviews-count').string
        if n_ratings:
            recipe['n_ratings'] = unidecode(n_ratings.strip())

        # get stats if available (e.g. yield, prep time, etc.)
        for item in soup.find_all('dd', class_=True):
            stat = item.string
            if stat:
                recipe[item.get('class')[0]] = unidecode(stat.strip())

        recipe['ingredients'] = []
        for item in soup.find_all('li', class_='ingredient'):
            ingredient = item.string
            if ingredient:
                recipe['ingredients'].append(unidecode(ingredient.strip()))

        recipe['instructions'] = []
        for item in soup.find_all('li', class_='preparation-step'):
            instruction = item.string
            if instruction:
                instruction = instruction.strip()
                recipe['instructions'].append(unidecode(instruction.strip()))
    except:
        logging.error('ENCOUNTERED A PROBLEM SCRAPING %s, SKIPPING...', url)

    return recipe

with open(RECIPE_LINKS_FP, 'r') as f:
    recipe_links = [line.strip() for line in f]

# distribute to different processes to scrape asynchronously
pool = Pool(processes=10)
recipes = pool.map(get_recipe, recipe_links)

# remove recipes that were not scraped properly
recipes = [recipe for recipe in recipes
           if 'ingredients' in recipe and 'instructions' in recipe]

with open(OUTPUT_FP, 'w') as f:
    json.dump(recipes, f)
