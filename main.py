from selenium import webdriver
from bs4 import BeautifulSoup
import simplejson as json
from time import sleep
from random import random


def write_file(data):
    # Writes recipes to the output file "output.txt"
    path = "output.txt"
    f = open(path, "w")
    json.dump(data, f, indent=2)
    f.close()


def get_ratings(ratings_element):
    # Determines how many stars are present for a given recipe, default is set to 0.0 if no ratings are given
    star_count = 0.0
    if ratings_element is not None:
        for rating in ratings_element.children:
            if rating['class'] == ['full-star']:
                star_count += 1
            elif rating['class'] == ['half-star']:
                star_count += 0.5
    return star_count


def get_ingredients(ingredient_list):
    # Creates an array of ingredients with whitespaces stripped from result
    ingredients = []
    for ingredient in ingredient_list:
        ingredients.append(ingredient.get_text(" ", strip=True))
    return ingredients


def create_recipe_object(driver, recipe_link):
    # Function visits recipe link and creates recipe object with fields extracted from page
    driver.get(recipe_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    recipe = {}
    recipe['recipeUrl'] = recipe_link
    recipe['recipeName'] = soup.find(
        'h1', {'class': 'recipe-title'}).get_text()
    recipe['recipePhoto'] = soup.find(
        'div', {'class': 'recipe-details-image'}).find('img').get('src')
    recipe['ingredients'] = get_ingredients(
        soup.findAll('li', {'class': 'IngredientLine'}))
    recipe['ratings'] = get_ratings(
        soup.find('a', {'class': 'recipe-details-rating'}))
    recipe['cookTime'] = soup.findAll(
        'div', {'class': 'recipe-summary-item'})[1].get_text(" ")
    recipe['serve'] = int(soup.find(
        'div', {'class': 'servings'}).find('input').get('value'))
    return recipe


def yummly_crawler(driver, num_recipes):
    # Function takes Selenium browser instance of Yummly.com and creates a recipe object from each recipe link
    domain = 'https://www.yummly.com'
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    recipes = []

    # Extracts recipe information from links and adds new recipe objects to array up to specified num_recipes for writing to output file
    recipe_links = soup.findAll('a', {'class': 'card-title'})
    for link in recipe_links:
        if len(recipes) < num_recipes:
            recipe_link = link.get('href')
            new_recipe = create_recipe_object(driver, domain + recipe_link)
            recipes.append(new_recipe)
    write_file(recipes)


def scroll_down_page(driver, scroll_height, scroll_count):
    # Uses browser scrollHeight to scroll Selenium browser instance and load more recipes
    driver.execute_script(
        f'const appContent = document.querySelector(\'.app-content\'); appContent.scrollTo(0, {scroll_height * scroll_count});')
    # Mock user behavior by randomizing wait times
    sleep(random() * 3)


def infinite_scroll(driver, num_recipes):
    # Scrolls the instance of the Selenium browser to validate the correct number of recipes are loaded on the page
    scroll_count = 1
    items = driver.execute_script(
        'return document.querySelectorAll(\'.recipe-card\').length;')
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    # Checks number of recipes loaded in Selenium browser instance and calls scroll_down_page if more recipes need to be loaded
    while (items < num_recipes):
        scroll_down_page(driver, scroll_height, scroll_count)
        items = driver.execute_script(
            'return document.querySelectorAll(\'.recipe-card\').length;')
        scroll_count += 1


def start(num_recipes=100):
    # Main function that gets called to run web scraper and generate recipes output file
    # Default number of recipes is 100
    # Allows caching of resources for faster page loading
    chromeOptions = webdriver.ChromeOptions()
    prefs = {
        'disk-cache-size': 4096
    }
    chromeOptions.add_experimental_option('prefs', prefs)

    # Runs an instance of a browser through selenium and executes scrolling function to ensure the correct number of results are loaded
    driver = webdriver.Chrome(options=chromeOptions)
    driver.implicitly_wait(15)
    driver.get('https://www.yummly.com/recipes')
    infinite_scroll(driver, num_recipes)
    yummly_crawler(driver, num_recipes)
    driver.quit()


# Update NUM_RECIPES to change how many recipes are returned
# To run web scraper execute "python3 main.py" in terminal, results will be added to output.txt file
NUM_RECIPES = 100
start(NUM_RECIPES)
