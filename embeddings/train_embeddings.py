from gensim.models import Word2Vec
import json
import logging
import nltk.data

logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', level=logging.INFO)

RECIPES_FP = '../recipes.json'
MODEL_FOLDER_FP = 'models'
MODEL_FP = '{}/embeddings.model'.format(MODEL_FOLDER_FP)

logging.info('LOADING RECIPES...')
with open(RECIPES_FP, 'r') as f:
    recipes = json.load(f)
logging.info('LOADING COMPLETE.')

# import NLTK sentence tokenizer
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

# split each step of recipe instructions into individual sentences, then tokenize
instructions = []
for recipe in recipes:
    for instruction in recipe['instructions']:
        steps = tokenizer.tokenize(instruction)  # sentence tokenizer
        for step in steps:
            instructions.append(nltk.word_tokenize(step))  # word tokenizer
logging.info('NUMBER OF SENTENCES OF INSTRUCTIONS: %d', len(instructions))

# train word2vec model
logging.info('TRAINING WORD2VEC MODEL...')
model = Word2Vec(instructions, min_count=2, size=100)
logging.info('TRAINING COMPLETE.')

# save model to file
model.wv.save(MODEL_FP)
