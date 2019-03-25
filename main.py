from selenium import webdriver
from bs4 import BeautifulSoup
import simplejson as json
from time import sleep
from random import random


def yummily_crawler(driver, num_items):
    domain = 'https://www.yummly.com'
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    recipes = []

    # Extracts correct number of links to recipes and adds created recipe objects to array for writing to output file
    for link in soup.findAll('a', {'class': 'card-title'}):
        if len(recipes) < num_items:
            recipe_link = link.get('href')
            new_recipe = create_recipe_object(driver, domain + recipe_link)
            recipes.append(new_recipe)
    write_file(recipes)


def create_recipe_object(driver, link):
    driver.get(link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Creates recipe object with fields extracted from HTML
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
    return new_recipe


def get_ratings(ratings):
    # Determines how many stars are present for a given recipe, default is set to 0.0 if no ratings are given
    count = 0.0
    if ratings is not None:
        for rating in ratings.children:
            if rating['class'] == ['full-star']:
                count += 1
            elif rating['class'] == ['half-star']:
                count += 0.5
    return count


def get_ingredients(ingredient_list):
    # Creates an array of ingredients with whitespaces stripped from result
    ingredients = []
    for ingredient in ingredient_list:
        ingredients.append(ingredient.get_text(" ", strip=True))
    return ingredients


def write_file(data):
    # Writes recipes to the output file
    path = "output.txt"
    f = open(path, "w")
    json.dump(data, f, indent=2)
    f.close()


def infinite_scroll(driver, num_items):
    # Scrolls the instance of the selenium browser validate the correct number of recipes are loaded on the page
    scroll_count = 1
    items = driver.execute_script(
        'return document.querySelectorAll(\'.recipe-card\').length;')
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    while (items <= num_items):
        driver.execute_script(
            f'const appContent = document.querySelector(\'.app-content\'); appContent.scrollTo(0, {scroll_height * scroll_count});')
        items = driver.execute_script(
            'return document.querySelectorAll(\'.recipe-card\').length;')
        sleep(random() * 3)
        scroll_count += 1


def start(num_items=100):
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
    infinite_scroll(driver, num_items)
    yummily_crawler(driver, num_items)
    driver.quit()


# Update NUM_ITEMS to change how many recipes are returned
# To run web scraper execute "python3 main.py" in terminal, results will be added to output.txt file
NUM_ITEMS = 100
start(NUM_ITEMS)
