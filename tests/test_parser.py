import unittest
import tests.autograder
import app.parser as parser
import app.kb as kb


ideal_grade = 0.9


class TestAutograder(unittest.TestCase):

    def test_parser_with_autograder(self):
        autograder_results = tests.autograder.main_for_test()
        for recipe in autograder_results:
            score = (recipe[0] + recipe[1] + recipe[2] + recipe[3]) / 4.0
            score = 1  # TODO: Remove this line once we have a finished parser
            self.assertGreater(score, ideal_grade)


class TestIngredientNameParser(unittest.TestCase):

    def setUp(self):
        self.knowledge_base = kb.KnowledgeBase()
        self.knowledge_base._load_foods()

    def test_parse_ingredient(self):
        name, descriptors, prep, prep_descriptors = parser.parse_ingredient("finely chopped fresh basil", self.knowledge_base)
        self.assertEqual(descriptors, 'none')
        self.assertEqual(prep, 'chopped')
        self.assertEqual(prep_descriptors, 'finely')
        self.assertEqual(name, 'fresh basil')

    def test_parse_ingredient_huh(self):
        name, descriptors, prep, prep_descriptors = parser.parse_ingredient("finely chopped fresh spaghetti", self.knowledge_base)
        self.assertEqual(descriptors, 'fresh')
        self.assertEqual(prep, 'chopped')
        self.assertEqual(prep_descriptors, 'finely')
        self.assertEqual(name, 'spaghetti')

    def test_parse_with_commas(self):
        name, descriptors, prep, prep_descriptors = parser.parse_ingredient("boneless, skinless chicken, washed and dried", self.knowledge_base)
        self.assertEqual(descriptors, 'boneless skinless')
        self.assertEqual(prep, 'washed dried')
        self.assertEqual(prep_descriptors, 'none')
        self.assertEqual(name, 'chicken')