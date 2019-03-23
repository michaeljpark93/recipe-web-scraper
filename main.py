import requests
from bs4 import BeautifulSoup
import simplejson as json


def yummily_crawler():
    domain = 'https://www.yummly.com'
    url = domain + '/recipes'
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    recipes = []

    for link in soup.findAll('a', {'class': 'card-title'}):
        recipe_link = link.get('href')
        new_recipe = create_recipe_object(domain + recipe_link)
        recipes.append(new_recipe)
    write_file(recipes)


def create_recipe_object(link):
    source_code = requests.get(link)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    new_recipe = {}
    new_recipe['recipeUrl'] = link
    new_recipe['recipeName'] = soup.find(
        'h1', {'class': 'recipe-title'}).get_text()
    new_recipe['recipePhoto'] = soup.find(
        'div', {'class': 'recipe-details-image'}).find('img').get('src')
    new_recipe['ingredients'] = get_ingredients(
        soup.findAll('li', {'class': 'IngredientLine'}))
    new_recipe['ratings'] = get_ratings(
        soup.find('a', {'class': 'recipe-details-rating'}))
    new_recipe['cookTime'] = soup.findAll(
        'div', {'class': 'recipe-summary-item'})[1].get_text(" ")
    new_recipe['serve'] = int(soup.find(
        'div', {'class': 'servings'}).find('input').get('value'))

    # Bonus: add tags and recipe type to recipe item
    # new_recipe['tags'] = get_recipe_tags(
    #     soup.findAll('li', {'class': 'recipe-tag'}))
    # new_recipe['recipeType'] = get_recipe_type(
    #     soup.findAll('li', {'class': 'recipe-tag'}))
    return new_recipe


def get_ratings(ratings):
    count = 0.0
    if ratings is not None:
        for rating in ratings.children:
            if rating['class'] == ['full-star']:
                count += 1
            elif rating['class'] == ['half-star']:
                count += 0.5
    return count


def get_ingredients(ingredient_list):
    ingredients = []
    for ingredient in ingredient_list:
        ingredients.append(ingredient.get_text(" ", strip=True))
    return ingredients


# def get_recipe_tags(tag_list):
#     tags = []
#     for tag in tag_list:
#         tags.append(tag['title'])
#     return tags


# def get_recipe_type(tag_list):
#     recipeTypes = {"Main Dishes", "Beverages", "Breakfast", "Desert", "Salad"}
#     types = []
#     for tag in tag_list:
#         if tag in recipeTypes:
#             types.append(tag)
#     return types


# Write results to the output file
def write_file(data):
    path = "output.txt"
    f = open(path, "w")
    json.dump(data, f, indent=2)
    f.close()


yummily_crawler()
