import unittest

from legaliser import legalise, Many, Optional, AnyType
from legaliser import LegaliserTypeException, LegaliserValueException
from legaliser import LegaliserKeysNotPresentException, LegaliserTooManyKeysPresentException
from legaliser import LegaliserCriteriaException, LegaliserCriteriaOtherException


class TestBase(unittest.TestCase):
    def assertException(self, exception, msg, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except exception as e:
            self.assertEqual(e.message, msg)
        else:
            self.assertTrue(False, 'This should have raised {} with {}'.format(exception, msg))


class BasicTests(TestBase):
    def test_basics(self):
        legalise({})
        legalise({}, dict)
        legalise({"key": 5}, dict)
        legalise({"k1": 2, "k2": 155}, dict)
        legalise({"k1": 2, "k2": 155}, {'k1': int, 'k2': int})
        legalise({"k1": 2, "k2": False}, {'k1': int, 'k2': bool})
        legalise({"k1": 2, "k2": False}, {'k1': int, 'k2': False})
        legalise({"k1": 2, "k2": None}, {'k1': int, 'k2': type(None)})
        legalise({"k1": 2, "k2": 155}, {'k1': int, 'k2': AnyType})
        legalise({"k1": 2, "k2": "v"}, {'k1': int, 'k2': AnyType})
        legalise({"k1": 2, "k2": False}, {'k1': int, 'k2': AnyType})
        legalise({"k1": 2, "k2": None}, {'k1': int, 'k2': AnyType})

    def test_dict_value(self):
        legalise({"key": 5}, {'key': int})
        legalise({"key": 5}, {'key': 5})
        self.assertException(LegaliserTypeException, 'At .key expecting type str, got "5" of int type instead',
                             legalise, {"key": 5}, {'key': str})
        self.assertException(LegaliserValueException, 'At .key expecting value of "7", got "5" instead',
                             legalise, {"key": 5}, {'key': 7})
        self.assertException(LegaliserKeysNotPresentException, 'At . expecting key "q", but not found',
                             legalise, {"key": 5}, {'key': 7, 'q': False})
        self.assertException(LegaliserTooManyKeysPresentException, 'At . not expected key "key" found',
                             legalise, {"key": 5, "q": 5}, {'q': int})
        self.assertException(LegaliserKeysNotPresentException, 'At . expecting key "q", but not found',
                             legalise, {"key": 5}, {'q': 7})
        self.assertException(LegaliserTooManyKeysPresentException, 'At . not expected key "key" found',
                             legalise, {"key": 0}, {})
        self.assertException(LegaliserKeysNotPresentException, 'At . expecting key "q", but not found',
                             legalise, {}, {'q': 7})
        legalise({"key": 5}, {'key': (int, lambda x: x < 9)})
        self.assertException(LegaliserCriteriaException, 'At .key function <lambda> failed',
                             legalise, {"key": 5}, {'key': (int, lambda x: x < 3)})
        legalise({"k1": 2, "k2": 17}, {'k1': int, 'k2': (int, Optional)})
        legalise({"k1": 2}, {'k1': int, 'k2': (int, Optional)})
        self.assertException(LegaliserTooManyKeysPresentException, 'At . not expected key "k3" found',
                             legalise, {"k1": 5, "k3": 0}, {'k1': int, 'k2': (int, Optional)})

        def criteria(x):
            return x < 4
        legalise({"key": 2}, {'key': (int, criteria)})
        self.assertException(LegaliserCriteriaException, 'At .key function criteria failed',
                             legalise, {"key": 5}, {'key': (int, criteria)})

    def test_dict_values(self):

        def odd_values(x):
            for v in x.values():
                if v % 2 == 0:
                    return False
            return True
        legalise({"key": 5}, (dict, odd_values))
        legalise({"key": 5, "bla": 17}, (dict, odd_values))
        self.assertException(LegaliserCriteriaException, 'At . function odd_values failed',
                             legalise, {"key": 5, "bla": 18}, (dict, odd_values))
        self.assertException(LegaliserCriteriaOtherException,
                             'At . function odd_values failed raising: '
                             'TypeError("unsupported operand type(s) for %: \'list\' and \'int\'",)',
                             legalise, {"key": 5, "bla": []}, (dict, odd_values))


class ComplexTests(TestBase):
    def test_list_with_many(self):
        j = {
            "a": 5,
            "b": [1, 3, "s"],
            "c": [2, 4, 8]
        }

        s = {'a': int,
             'b': (list, lambda x: 0 < len(x) < 4),
             'c': [Many(int)]}
        legalise(j, s)
        self.assertException(LegaliserCriteriaException, 'At .b function <lambda> failed',
                             legalise, {"a": 5, "b": [], "c": []}, s)
        self.assertException(LegaliserTypeException,
                             'At .c expecting type int, got "s" of {} type instead'.format(str.__name__),
                             legalise, {"a": 5, "b": [1], "c": ["s"]}, s)

    def test_list_with_many_and_criteria(self):
        s = {'c': ([Many({'a': int})], lambda x: len(x) < 3)}
        legalise({"c": [{"a": 1}]}, s)
        self.assertException(LegaliserCriteriaException, 'At .c function <lambda> failed',
                             legalise, {"c": [{"a": 3}, {"a": 5}, {"a": 7}]}, s)


if __name__ == '__main__':
    unittest.main()
