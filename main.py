import requests
import simplejson as json
from time import sleep
from random import random


def write_file(data):
    # Writes recipes to the output file "output.txt" in json format
    path = "output.txt"
    f = open(path, "w")
    json.dump(data, f, indent=2)
    f.close()


def get_ingredients(ingredient_list):
    # Creates an list of ingredients from the recipe by extracting 'wholeLine' key from each ingredient object
    ingredients = []
    for ingredient in ingredient_list:
        ingredients.append(ingredient['wholeLine'])
    return ingredients


def get_tag_details(tag_list, tag_key):
    # Helper function for get_tags method to extract different tags by tag_key
    tag_details = []
    if tag_list.get(tag_key):
        for tag in tag_list[tag_key]:
            tag_details.append(tag['display-name'])
    return tag_details


def get_tags(tag_list):
    # Creates a list of tags from the recipe by calling get_tag_details and passing in the tag object key
    difficulty = get_tag_details(tag_list, 'difficulty')
    nutrition = get_tag_details(tag_list, 'nutrition')
    technique = get_tag_details(tag_list, 'technique')
    recipe_tags = difficulty + nutrition + technique
    return recipe_tags


def get_recipe_type(recipe_type_list):
    # Creates a list of recipe type categories by extracting the course information from the recipe object
    recipe_types = []
    if recipe_type_list.get('course'):
        for recipe_type in recipe_type_list['course']:
            recipe_types.append(recipe_type['display-name'])
    return recipe_types


def create_recipe_object(recipe_object):
    # Helper function creates recipe dictionary with correct fields extracted from the recipe json object
    recipe_content = recipe_object['content']
    recipe_display = recipe_object['display']
    recipe = {}
    recipe['recipeUrl'] = recipe_content['details']['attribution']['url']
    recipe['recipeName'] = recipe_display['displayName']
    recipe['recipePhoto'] = recipe_display['images'][0]
    recipe['ingredients'] = get_ingredients(recipe_content['ingredientLines'])
    recipe['ratings'] = recipe_content['reviews']['averageRating']
    recipe['cookTime'] = recipe_content['details']['totalTime']
    recipe['serve'] = recipe_content['details']['numberOfServings']
    # Bonus fields 
    recipe['tags'] = get_tags(recipe_content['tags'])
    recipe['recipeType'] = get_recipe_type(recipe_content['tags'])
    return recipe


def yummly_crawler(recipe_data, recipes_store, searched_recipes):
    # Creates and appends recipe objects to be written to the output.txt file
    # Sends appropriate recipe json object to the create_recipe_object function
    recipe_list = recipe_data.get('feed')
    # Error checking to make sure that correct data is received
    if recipe_list is None:
        return
    for recipe_object in recipe_list:
        # Checks if recipe has already been visited by storing recipe_ids in searched_recipes
        recipe_id = recipe_object['content']['details']['id']
        if recipe_id not in searched_recipes:
            new_recipe = create_recipe_object(recipe_object)
            recipes_store.append(new_recipe)
            searched_recipes.add(recipe_id)


def make_yummly_request(recipe_start):
    # Makes AJAX request to Yummly with start parameter updated on each iteration and return json response
    url = 'https://mapi.yummly.com/mapi/v16/content/search'
    params = {
        'solr.seo_bost': 'new',
        'start': f'{recipe_start}',
        'maxResult': '36',
        'fetchUserCollections': 'false',
        'allowedContent': 'related_search',
        'guided-search': 'true',
        'solr.view_type': 'search_internal',
    }
    # Handle network errors
    for attempt in range(5):
        try:
            response = requests.get(
                url=url,
                params=params,
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            continue


def start(min_num_recipes=100):
    # Main function that gets called and verifies that at least the minimum number of recipes are extracted
    recipe_start_idx = 0
    # Store holds all the recipes for output to text file
    recipes_store = []
    # Searched recipes ensures that duplicate recipes are not included in final output
    searched_recipes = set()

    while min_num_recipes > len(recipes_store):
        # data holds json response from AJAX request, data is then passed to yummly crawler to extract recipe details
        data = make_yummly_request(recipe_start_idx)
        yummly_crawler(data, recipes_store, searched_recipes)
        recipe_start_idx += 36
        # Sleep mocks user behavior to avoid being blocked for spam
        sleep(random() * 3)
    print(f'Success! {len(recipes_store)} recipes have been scraped')
    write_file(recipes_store)


# Update MIN_NUM_RECIPES to get at least that many recipes
# To run web scraper execute "python3 main.py" in terminal, results will be added to output.txt file
MIN_NUM_RECIPES = 1000
start(MIN_NUM_RECIPES)
