import json
import logging
import subprocess

logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', level=logging.INFO)

RECIPES_FP = '../recipes.json'
INSTRUCTIONS_FOLDER_FP = 'data/instructions'
PARSED_FOLDER_FP = 'data/parsed'

with open(RECIPES_FP, 'r') as f:
    recipes = json.load(f)

for i, recipe in enumerate(recipes):
    instructions_str = ' '.join(recipe['instructions'])
    if instructions_str.count(' | ') > 3:  # fix case of long, unparseable sentences
        instructions_str = instructions_str.replace(' |', '.')

    instructions_fp = '{0}/{1}.txt'.format(INSTRUCTIONS_FOLDER_FP, i)
    with open(instructions_fp, 'w') as f:
        f.write(instructions_str + '\n')

    parse_tree = subprocess.check_output(['../stanford-parser-full-2018-10-17/lexparser.sh', instructions_fp])

    parsed_fp = '{0}/{1}.txt'.format(PARSED_FOLDER_FP, i)
    with open(parsed_fp, 'wb') as f:
        f.write(parse_tree)
