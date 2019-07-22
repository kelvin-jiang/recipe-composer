import json
import logging
from nltk.stem import WordNetLemmatizer
from unidecode import unidecode

logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', level=logging.INFO)

# manually-created list of common ingredients missing from the Yummly dataset
YUMMLY_MISSING = ['aperol', 'berries', 'blueberries', 'bourbon', 'boysenberries', 'brie',
                  'cashew', 'cheddar', 'cherries', 'cookies', 'cornstarch', 'cranberries',
                  'feta', 'grand marnier', 'gruyere', 'half and half', 'half-and-half',
                  'mayonnaise', 'parmesan', 'pecorino', 'pimm\'s no. 1', 'raspberries',
                  'romaine', 'romano', 'strawberries', 'tabasco', 'turmeric', 'yogurt']
YUMMLY_FPS = ['data/yummly-dataset/train.json', 'data/yummly-dataset/test.json']
BAD_PREFIXES = ['fresh', 'large', 'small']
RECIPES_FP = '../recipes.json'
OUTPUT_FP = 'data/recipe_ingredients.json'

ingredients_dataset = set(YUMMLY_MISSING)
lemmatizer = WordNetLemmatizer()
recipe_ingredients = {}

# load and normalize ingredients from yummly dataset
logging.info('LOADING YUMMLY DATASET (+ MORE)...')
for fp in YUMMLY_FPS:
    with open(fp, 'r') as f:
        yummly_json = json.load(f)

    for recipe in yummly_json:
        for full_ingredient in recipe['ingredients']:
            full_ingredient = unidecode(full_ingredient).lower()
            full_ingredient = full_ingredient.split(',')[0].strip()  # remove words after comma
            full_ingredient = lemmatizer.lemmatize(full_ingredient)
            # remove bad prefix if exists
            for prefix in BAD_PREFIXES:
                if full_ingredient.startswith(prefix):
                    full_ingredient = full_ingredient[len(prefix):].strip()

            if full_ingredient:
                ingredients_dataset.add(full_ingredient)
logging.info('LOADING COMPLETE. NUMBER OF INGREDIENTS: %d', len(ingredients_dataset))

# find best ingredient candidate for ingredients in recipes
logging.info('LOADING RECIPES...')
with open(RECIPES_FP, 'r') as f:
    recipes = json.load(f)
logging.info('LOADING COMPLETE.')

for recipe in recipes:
    ingredients = []
    for full_ingredient in recipe['ingredients']:
        full_ingredient = full_ingredient.lower()
        candidates = [cand for cand in ingredients_dataset if cand in full_ingredient]
        if len(candidates) == 0:
            # probably not a food ingredient (e.g. cooking utensil), skip
            continue

        # use longest matching candidate as ingredient
        ingredient = sorted(candidates, key=len, reverse=True)[0]
        ingredients.append(ingredient)

    recipe_ingredients[recipe['url']] = ingredients
    logging.info('%s -> %s', recipe['ingredients'], ingredients)

with open(OUTPUT_FP, 'w') as f:
    json.dump(recipe_ingredients, f)
