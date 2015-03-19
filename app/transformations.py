import recipe
from enums import FoodGroup
from parser import get_html


def to_vegan(knowledge_base, from_recipe):
    """
    Takes a Recipe input and output vegan Recipe.
    First, fun the to_vegetarian function.
    Loop through ingredients, checking food group (look in enums.py) for no-no groups. If the ingredient is of
    a no-no-group, check for a substitution in kb.vegan_substitutions (not yet written). If no suitable substitution
    can be found, replace with a quantity of TVP of equal weight.
    :param from_recipe: knowledge_base, old recipe
    :return: new recipe
    """
    # print "Testing Vegan: "
    old_title = from_recipe.title
    from_recipe = to_vegetarian(knowledge_base, from_recipe)

    for ingredient in from_recipe.ingredients:
        if ingredient.food_type is not None:
            if ingredient.food_type.food_group in FoodGroup.DAIRY_AND_EGG_PRODUCTS:
                # Look for substitution in kb.vegetarian_substitutes
                for sub in knowledge_base.vegan_substitutions:
                    for item in range(len(from_recipe.ingredients)):
                        if sub.food_in.name in from_recipe.ingredients[item].name:
                            subbed_ingredient = from_recipe.ingredients[item].name
                            # print "item to sub: " + from_recipe.ingredients[item].name
                            # print "replace with: " + sub.food_out[0].name
                            from_recipe.ingredients[item] = sub.food_out[0]
                            from_recipe.ingredients[item].match_to_food(knowledge_base)
                            # print "subbed"
                            for step_num in range(len(from_recipe.steps)):
                                from_recipe.steps[step_num] = from_recipe.steps[step_num].replace(subbed_ingredient,
                                                                                                  sub.food_out[0].name)
    # for i in from_recipe.ingredients:
    #     print i.name
    # for s in range(len(from_recipe.steps)):
    #    print from_recipe.steps[s]

    from_recipe.change_title('Vegan ' + old_title)
    return from_recipe


def to_vegetarian(knowledge_base, from_recipe):
    """
    Takes a Recipe input and output vegetarian Recipe.
    Loop through ingredients, checking food group (look in enums.py) for no-no groups. If the ingredient is of a
    no-no-group, check for a substitution in kb.vegetarian_substitutions (not yet written). If no suitable substitution
    can be found, replace with a quantity of TVP of equal weight.
    :param from_recipe: knowledge_base, old recipe
    :return: new recipe
    """
    # print "Testing Vegetarian: "
    for ingredient in from_recipe.ingredients:
        if ingredient.food_type is not None:
            if ingredient.food_type.food_group in (FoodGroup.POULTRY_PRODUCTS, FoodGroup.SAUSAGES_AND_LUNCHEON_MEATS,
                                                   FoodGroup.PORK_PRODUCTS, FoodGroup.BEEF_PRODUCTS,
                                                   FoodGroup.FINFISH_AND_SHELLFISH_PRODUCTS,
                                                   FoodGroup.LAMB_VEAL_AND_GAME_PRODUCTS):
                # Look for substitution in kb.vegetarian_substitutes
                for sub in knowledge_base.vegetarian_substitutions:
                    for item in range(len(from_recipe.ingredients)):
                        if sub.food_in.name in from_recipe.ingredients[item].name:
                            subbed_ingredient = from_recipe.ingredients[item].name
                            # print "item to sub: " + from_recipe.ingredients[item].name
                            # print "replace with: " + sub.food_out[0].name
                            from_recipe.ingredients[item] = sub.food_out[0]
                            from_recipe.ingredients[item].match_to_food(knowledge_base)
                            # print "subbed"
                            for step_num in range(len(from_recipe.steps)):
                                from_recipe.steps[step_num] = from_recipe.steps[step_num].replace(subbed_ingredient,
                                                                                                  sub.food_out[0].name)
        # for i in from_recipe.ingredients:
        #     print i.name
    # for s in range(len(from_recipe.steps)):
    #    print from_recipe.steps[s]

    old_title = from_recipe.title
    from_recipe.change_title('Vegetarian ' + old_title)
    return from_recipe


def make_healthy(from_recipe, knowledge_base):
    """
    STUB DESCRIPTION:
    Write make_healthy function to take a Recipe input and output a healthier Recipe.
    Loop through Ingredients in Recipe, and apply USDA lookup function from #62.
    Think of other ways also.
    :param from_recipe: old recipe
    :return: new recipe
    """
    new_recipe = recipe.Recipe('Healthy ' + from_recipe.title, steps=from_recipe.steps)
    for i in range(len(from_recipe.ingredients)):
        if # healthy version in kb:
            new_recipe.ingredients[i] = from_recipe.ingredients[i]
            new_recipe.ingredients[i].name += ' low'
            match_to_food(knowledge_base)
        else:
            new_recipe.ingredients[i] = from_recipe.ingredients[i]
    return from_recipe


def make_unhealthy(from_recipe, knowledge_base):
    """
    STUB DESCRIPTION:
    Take a Recipe input, and return a Recipe that has been made unhealthy.
    For each Ingredient in the Recipe, query the USDA database for similar foods, and choose the least healthy alternative.
    If no changes can be found, add Cheese Whiz.
    :param from_recipe: old recipe
    :return: new recipe
    """
    q = knowledge_base.interpret_quantity('1 can')
    cheez = recipe.Ingredient('Cheez Whiz', q)
    cheez.match_to_food(knowledge_base)

    from_recipe.ingredients.append(cheez)
    from_recipe.steps.append('Garnish with Cheez Whiz as desired. Spray Cheez Whiz directly into mouth.')

    return from_recipe


def lookup_healthy_ingredient(from_ingredient, knowledge_base):
    """
    STUB DESCRIPTION:
    Write a function that takes an Ingredient input and outputs a healthier Ingredient, using simple search terms
    like "low fat," if it finds one in the USDA. If no result is found, return None.
    :param from_ingredient:
    :return: Ingredient, or None
    """
    n = from_ingredient.name
    if knowledge_base.lookup_food('low fat '+n):

    if knowledge_base
    return from_ingredient


def lookup_alternative_recipe(original_recipe_name, unavailable_ingredient_list):
    """
    STUB DESCRIPTION:
    Write lookup_alternative_recipe function to take args: Recipe, list of unavailable Ingredients
    (returned from transform_availability #60)
    It should query allrecipes.com using the advanced search to specify the recipe title and missing ingredients.
    If helper functions are needed, write them as stubs and make new issues for them.
    :param original_recipe_name: Title string from recipe to be replaced
    :param unavailable_ingredient_list: unavailable ingredients list
    :return: new recipe URL
    """
    url = 'http://allrecipes.com/search/default.aspx?ms=0&origin=Home+Page&rt=r&qt=i&wt='
    url += original_recipe_name.replace(' ', '%20')
    url += '&pqt=i&fo=0'
    for j in range(len(unavailable_ingredient_list)):
        url += '&u' + str(j) + '=' + str(unavailable_ingredient_list[j].replace(' ', '%20'))
    return url


def transform_availability(old_recipe, old_ingredient, kb):
    """
    STUB DESCRIPTION:
    Write transform_availability function to take an Ingredient argument and return a list of Ingredient objects
    that are possible substitutions, complete with quantity info.
    First check our knowledge base for common substitutions, then move on to using nutritional data / food group to
    find suitable alternatives.
    Make new issues for any useful helper functions.
    :param old_recipe: recipe containing ingredient
    :param old_ingredient: ingredient to transform
    :return: list of possible substitution Ingredient objects
    """
    pass
    subs = kb.substitutions
    possible_substitutions = []
    for sub in subs:
        if sub.food_in.name == old_ingredient.food.name:
            possible_substitutions.append(sub.food_out)
    if not possible_substitutions:
        pass
    return possible_substitutions