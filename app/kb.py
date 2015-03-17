# All code relating to the system's knowledge base goes here
# The KnowledgeBase class contains the data itself
# All other methods are just useful helper functions

from compiler.ast import flatten
import nltk

from enums import Nutrient
from enums import FoodGroup
import util
import parser
import regex
import recipe


class KnowledgeBase:
    def __init__(self):
        self.foods = []
        self.cooking_terms = set()
        self.cooking_wares = set()
        self.measurements = {}
        self.common_substitutions = []
        self.italian_style = []
        self.mexican_style = []
        self.east_asian_style = []
        self.vegetarian_substitutions = []
        self.vegan_substitutions = []

    def load(self):
        """
        Loads parsed knowledge base data from modifiable data text files into global fields
        Typically called right after object initialization
        """
        self._load_foods()
        util.vprint('Loading cooking terminology')
        self._load_cooking_terms()
        self._load_cooking_wares()
        self._load_measurements()
        self._load_common_substitutions()
        self._load_style_tags()
        self._load_style_substitutions()
        util.vprint('Finished loading:')
        util.vprint('\t%s foods' % str(len(self.foods)))
        util.vprint('\t%s cooking wares' % str(len(self.cooking_wares)))
        util.vprint('\t%s measurements' % str(len(self.measurements)))
        util.vprint('\t%s common substitutions' % str(len(self.common_substitutions)))
        util.vprint('\t%s Italian substitutions' % str(len(self.italian_style)))
        util.vprint('\t%s Mexican substitutions' % str(len(self.mexican_style)))
        util.vprint('\t%s East Asian substitutions' % str(len(self.east_asian_style)))
        util.vprint('\t%s vegan substitutions' % str(len(self.vegan_substitutions)))
        util.vprint('\t%s vegetarian substitutions' % str(len(self.vegetarian_substitutions)))

    def _load_foods(self):
        util.vprint('Loading nutrient data')
        nutritional_data = self._load_nutritional_data()
        util.vprint('Loading food data')
        with open(util.relative_path('kb_data/sr27asc/FOOD_DES.txt')) as food_des_txt:
            food_des_lines = food_des_txt.readlines()
            for food_des_line in food_des_lines:
                parsed_line = parse_usda_line(food_des_line)
                new_food = Food(parsed_line[0], parsed_line[1], parsed_line[2])
                if new_food.food_group in food_group_blacklist:
                    continue
                if new_food.food_id in food_id_blacklist:
                    continue
                bad_food_name = False
                for keyword_group in food_keyword_blacklist:
                    for keyword in keyword_group:
                        if keyword in new_food.name:
                            bad_food_name = True
                if bad_food_name:
                    util.vprint("Skipping " + new_food.name)
                    continue
                if new_food.food_id in nutritional_data:
                    new_food.nutritional_data = nutritional_data[new_food.food_id]
                self.foods.append(new_food)

    def _load_cooking_terms(self):
        self.cooking_terms = set(read_txt_lines_into_list('kb_data/cooking_terms.txt'))

    def _load_cooking_wares(self):
        self.cooking_wares = set(read_txt_lines_into_list('kb_data/cooking_wares.txt'))

    def _load_measurements(self):
        raw_measurement_list = read_txt_lines_into_list('kb_data/measurements.txt')
        for raw_measurement in raw_measurement_list:
            parsed_in_out = raw_measurement.split('=')
            full_name = parsed_in_out.pop(0).strip()
            if parsed_in_out:
                if not parsed_in_out[0]:
                    parsed_in_out = []
                else:
                    parsed_in_out = parsed_in_out[0].split(',')
                abbreviation_list = parsed_in_out
            else:
                abbreviation_list = []
            self.measurements[full_name] = abbreviation_list

    def _load_common_substitutions(self):
        raw_sub_list = read_txt_lines_into_list('kb_data/common_substitutions.txt')
        for raw_sub in raw_sub_list:
            parsed_in_out = raw_sub.split('=')
            if len(parsed_in_out) != 2:
                util.warning('Incorrect substitution string: ' + raw_sub)
                continue
            if parsed_in_out[0][-1] == '*':
                self.common_substitutions.append(self._format_raw_sub(parsed_in_out[0][:-1], parsed_in_out[1], 'common'))
                self.common_substitutions.append(self._format_raw_sub(parsed_in_out[1], parsed_in_out[0][:-1], 'common'))
            else:
                self.common_substitutions.append(self._format_raw_sub(parsed_in_out[0], parsed_in_out[1], 'common'))

    def _format_raw_sub(self, raw_food_in, raw_food_out, reason):
        """
        Creates CommonSubstitution object from substitutable ingredient strings
        :param raw_food_in: String of the form "quantity measurement food"
        :param raw_food_out: Arbitrary-length "OR"-delimited string of the same form
        :return: CommonSubstitution object holding appropriate ingredient objects
        """
        # TODO: parse food name with function #26 parser.parse_ingredient(string, self)
        result = []
        buff = [raw_food_in] + raw_food_out.split('OR')
        buff = [r.strip() for r in buff]
        for food in buff:
            ff = food.split()
            quantity_string = 'unknown'
            food_string = 'unknown'
            for i in range(len(ff)):
                if ff[i] in self.measurements:
                    quantity_string = ff[:i]
                    food_string = ff[i:]
                    break

            if quantity_string == 'unknown':
                for i in range(len(ff), 0, -1):
                    if regex.lolnum.match(ff[i]):
                        quantity_string = ff[:i] + 'units'
                        food_string = ff[i:]
                        break
            q = self.interpret_quantity(quantity_string)
            n, d, p, pd = parser.parse_ingredient(food_string, self)
            result.append(recipe.Ingredient(name=n.lower(), quantity=q, preparation=p, prep_description=pd, descriptor=d))


            # parse = regex.qi.match(food)
            # p = ''
            # if parse:
            #     q = self.interpret_quantity(parse.group(1))
            #     toks = nltk.word_tokenize(parse.group(2))
            # else:
            #     toks = nltk.word_tokenize(food)
            #     for tok in toks:
            #         if regex.preparation.match(tok):
            #             p = tok
            #             toks.remove(tok)
            #     q = Quantity(1, 'unit')
            # n = ' '.join(toks)
            # # TODO: Zinger: solve tests
            # result.append(recipe.Ingredient(name=n.lower(), quantity=q, preparation=p))
        if len(result) > 1:
            return CommonSubstitution(result.pop(0), result, reason)
        else:
            return CommonSubstitution()

    @staticmethod
    def _load_nutritional_data():
        result = {}
        with open(util.relative_path('kb_data/sr27asc/NUT_DATA.txt')) as nut_data_txt:
            nut_data_lines = nut_data_txt.readlines()
            for nut_data_line in nut_data_lines:
                parsed_line = parse_usda_line(nut_data_line)
                food_id = parsed_line[0]
                nut_id = parsed_line[1]
                nut_data = parsed_line[2:]
                if nut_id not in nutritional_data_whitelist:
                    continue
                if food_id not in result:
                    result[food_id] = {}
                result[food_id][nut_id] = nut_data
        return result

    def _load_style_tags(self):
        """
        This method is outdated, as we are no longer using style tags in this way.
        But...maybe it'll be useful someday.
        """
        raw_style_list = read_txt_lines_into_list('kb_data/style_tags.txt')
        for raw_style in raw_style_list:
            parsed_in_out = raw_style.split('=')
            ingredient_name = parsed_in_out[0]
            styles = parsed_in_out[1]
            if len(parsed_in_out) != 2:
                util.warning('Incorrect style string: ' + raw_style)
                continue
            style_list = styles.split(',')
            positive_styles = []
            negative_styles = []
            for style in style_list:
                style = style.strip()
                if len(style):
                    if style[0] == '+':
                        positive_styles.append(style[1:])
                        continue
                    elif style[0] == '-':
                        negative_styles.append(style[1:])
                        continue
                util.warning('Incorrect style string: ' + raw_style)
            self._add_style_tags(ingredient_name, positive_styles, negative_styles)

    def _add_style_tags(self, ingredient_name, positive_styles, negative_styles):
        matching_foods = self.lookup_food(ingredient_name)
        for matching_food in matching_foods:
            matching_food.add_styles(positive_styles, negative_styles)

    def _load_style_substitutions(self):
        """
        Loads Italian, Mexican, South Asian, vegan, AND vegetarian text files into fields
        """
        # TODO: I feel really bad about the use of copied code, so a helper function could be good to write sometime.
        italian_sub_list = read_txt_lines_into_list('kb_data/italian_style.txt')
        mexican_sub_list = read_txt_lines_into_list('kb_data/mexican_style.txt')
        south_asian_sub_list = read_txt_lines_into_list('kb_data/east_asian_style.txt')
        vegan_sub_list = read_txt_lines_into_list('kb_data/vegan_substitutions.txt')
        vegetarian_sub_list = read_txt_lines_into_list('kb_data/vegetarian_substitutions.txt')
        for raw_sub in italian_sub_list:
            parsed_in_out = [thing.strip() for thing in raw_sub.split('=')]
            if len(parsed_in_out) != 2:
                util.warning('Incorrect substitution string: ' + raw_sub)
                continue
            self.italian_style.append(self._format_raw_sub(parsed_in_out[0], parsed_in_out[1], 'italian'))
        for raw_sub in mexican_sub_list:
            parsed_in_out = [thing.strip() for thing in raw_sub.split('=')]
            if len(parsed_in_out) != 2:
                util.warning('Incorrect substitution string: ' + raw_sub)
                continue
            self.mexican_style.append(self._format_raw_sub(parsed_in_out[0], parsed_in_out[1], 'mexican'))
        for raw_sub in south_asian_sub_list:
            parsed_in_out = [thing.strip() for thing in raw_sub.split('=')]
            if len(parsed_in_out) != 2:
                util.warning('Incorrect substitution string: ' + raw_sub)
                continue
            self.east_asian_style.append(self._format_raw_sub(parsed_in_out[0], parsed_in_out[1], 'east_asian'))
        for raw_sub in vegan_sub_list:
            parsed_in_out = [thing.strip() for thing in raw_sub.split('=')]
            if len(parsed_in_out) != 2:
                util.warning('Incorrect substitution string: ' + raw_sub)
                continue
            self.vegan_substitutions.append(self._format_raw_sub(parsed_in_out[0], parsed_in_out[1], 'vegan'))
        for raw_sub in vegetarian_sub_list:
            parsed_in_out = [thing.strip() for thing in raw_sub.split('=')]
            if len(parsed_in_out) != 2:
                util.warning('Incorrect substitution string: ' + raw_sub)
                continue
            self.vegetarian_substitutions.append(self._format_raw_sub(parsed_in_out[0], parsed_in_out[1], 'vegetarian'))

    def lookup_food(self, food_name):
        """
        Gets a list of foods that match a search string
        :param food_name: search string
        :return: list of foods in knowledge base
        """
        result = []
        ingredient_tokens = [token.lower() for token in nltk.word_tokenize(food_name)]
        for food in self.foods:
            ok = True
            for token in ingredient_tokens:
                if token not in food.name.lower():
                    ok = False
                    break
            if ok:
                result.append(food)
        return result

    def interpret_quantity(self, string):
        """
        Generates a new Quantity object with amount and unit fields filled in from the input string
        :param string: Of the form "x y" where x represents a quantity and y can be found in the measurements dict
        :return: Quantity
        """
        # TODO: use regex instead of split (#54)
        q = Quantity()
        s = string.split()
        if len(s) != 2:
            util.warning('Invalid quantity string: Must contain 1 amount/unit pair')
            q.amount = 1
            q.unit = 'unit'
            return q
        s = [t.strip() for t in s]
        q.amount = util.fraction_to_decimal(s[0])
        if s[1] in self.measurements:
            q.unit = s[1]
        if not q.unit:
            print 'Could not identify unit of measurement; assuming \'unit(s)\''
            q.unit = 'unit'
        return q


class Food:
    def __init__(self, food_id=None, food_group=None, name=None, nutritional_data=None):
        self.food_id = food_id
        self.food_group = food_group
        self.name = name
        self.nutritional_data = nutritional_data
        self.positive_tags = []
        self.negative_tags = []

    def add_styles(self, positive_styles, negative_styles):
        for style in positive_styles:
            if style in self.positive_tags:
                continue
            else:
                self.positive_tags.append(style)
        for style in negative_styles:
            if style in self.positive_tags:
                self.positive_tags.remove(style)
                raise RuntimeError("Food obj cannot have identical + and - tags")
            if style in self.negative_tags:
                continue
            else:
                self.negative_tags.append(style)


class CommonSubstitution:
    def __init__(self, food_in=None, food_out=None, reason=None):
        self.food_in = food_in
        self.food_out = food_out
        self.reason = reason


class Quantity:
    def __init__(self, amount=None, unit=None):
        self.amount = amount
        self.unit = unit


def read_txt_lines_into_list(file_name):
    """
    Given a filename, returns a list with each cell being a line from the file
    Lines that have no content or begin with a '#' (comments) are skipped
    Converts to lowercase
    :param file_name: filename of source
    :return: list of file lines
    """
    result = []
    with open(util.relative_path(file_name)) as source_file:
        source_lines = source_file.readlines()
        for line in source_lines:
            if len(line) and line[-1] == '\n':
                line = line[:-1]
            if len(line) and line[0] != '#':
                result.append(line.lower())
    return result


def parse_usda_line(text):
    """
    Parses USDA database text format into a list
    :param text: raw database text
    :return: list
    """
    if len(text) and text[-1] == '\n':
        text = text[:-1]
    if not len(text):
        return []
    result = text.split('^')
    for i in range(len(result)):
        if len(result[i]) and result[i][0] == '~':
            result[i] = result[i][1:-1]
        else:
            result[i] = string_to_number(result[i])
    return result


def string_to_number(string):
    """
    Attempts to transform a string into a number
    :param string: string to be cast to number
    :return: number representation of string
    """
    try:
        string_float = float(string)
    except ValueError:
        return string
    try:
        string_int = int(string)
    except ValueError:
        return string_float
    if string_int == string_float:
        return string_int
    return string_float


nutritional_data_whitelist = \
    [
        Nutrient.PROTEIN,
        Nutrient.FAT,
        Nutrient.STARCH,
        Nutrient.WATER,
        Nutrient.SUGAR,
        Nutrient.FIBER
    ]

food_group_blacklist = \
    [
        FoodGroup.BABY_FOODS,
        FoodGroup.BREAKFAST_CEREALS,
        FoodGroup.FAST_FOODS,
        FoodGroup.MEALS_ENTREES_AND_SIDE_DISHES,
        FoodGroup.RESTAURANT_FOODS
    ]

food_id_blacklist = \
    [

    ]

food_keyword_blacklist = \
    [
        ['frozen']
    ]  # Format each element as a list of keywords

food_id_blacklist = flatten(food_id_blacklist)
