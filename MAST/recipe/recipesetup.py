from ingredient import Ingredient

from MAST.utility import MASTObj
from MAST.utility import MASTError

ALLOWED_KEYS = {
                  'recipeFile'     : (str, 'sic.recipe', 'Personalized recipe file'),\
                  'inputOptions'   : (InputOptions, InputOptions(), 'Input options parsed using input parser'),\
               } 

class Recipe:
    def __init__(self):
        self.name            = None
        self.ingredients     = dict()
        self.dependency_dict = dict()

    def set_name(self, name):
        self.name = name

    def add_ingredient(self, ingredient_name, ingredient):
        self.ingredients[ingredient_name] = ingredient

    def get_ingredient(self, ingredient_name, ingredient):
        return self.ingredients.get(ingredient_name)

    def add_parent(self, ingredient_name, parent_name):
        self.dependency_dict.setdefault(self.ingredients[ingredient_name], list()).append(self.ingredients[parent_name])


class RecipeSetup(MASTObj):
    def __init__(self, **kwargs):
        MASTObj.__init__(self, ALLOWED_KEYS, **kwargs)
        self.recipe_file    = self.keywords['recipeFile']
        self.input_options  = self.keywords['inputOptions']

    def parse_recipe(self):
        '''Parses the input recipe file and takes 
           necessary info to setup the jobs
        '''
        f_ptr        = open(self.recipe_file, "r")
        recipe_obj   = Recipe()

        for line in f_ptr.readlines():
            line = line.strip()
            #validate the line
            if not line or line.startswith('#'):
                continue

            #split line into elts
            elts         = [elt.strip() for elt in line.split()]
            init_keyword = elts[0].lower()

            #recipe name
            if init_keyword == "recipe":
                recipe_obj.set_name(elts[1])
                continue

            #handle job keyword
            if init_keyword == "ingredient":
                ingredient = Ingredient(elts[1], elts[2], input_options)
                recipe_obj.add_ingredient(elts[1], ingredient)
                continue

            #handle parent keyword
            if init_keyword == "parent":
                parent_objs = []
                is_parent   = True
                for elt in elts:
                    if elt.lower() == "child":
                        is_parent = False
                        continue
                    if is_parent:
                        parent_objs.append(recipe_obj.get_ingredient(elt))
                    else:
                        for parent in parent_objs:
                            recipe_obj.add_parent(elt, parent)

        f_ptr.close()
        return recipe_obj

    def start(self):
        '''Starts the setup process, parse the recipe file
           Use the input options and recipe info to 
           create directories and classes required
        '''
        recipe_obj = self.parse_recipe()
        return recipe_obj

