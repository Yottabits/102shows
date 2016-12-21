import unittest

from helpers import verify
from helpers.exceptions import *


class TestVerifyNumeric(unittest.TestCase):
    def test_string_fails(self):
        self.assertRaises(InvalidParameters, verify.numeric, candidate="6.7")

    def test_out_of_bounds_fails(self):
        self.assertRaises(InvalidParameters, verify.numeric, candidate=3.98, minimum=5.0, maximum=10.0)

    def test_max_bounds_passes(self):
        self.assertIsNone(verify.numeric(candidate=5.123, minimum=1.0, maximum=10.0))

    def test_is_min_bound_passes(self):
        self.assertIsNone(verify.numeric(candidate=1.0, minimum=1.0, maximum=10.0))

    def test_is_max_bound_passes(self):
        self.assertIsNone(verify.numeric(candidate=10.0, minimum=1.0, maximum=10.0))


class TestVerifyNotNegativeNumeric(unittest.TestCase):
    def test_null_int_passes(self):
        self.assertIsNone(verify.not_negative_numeric(candidate=0))

    def test_null_float_passes(self):
        self.assertIsNone(verify.not_negative_numeric(candidate=0.0))

    def test_positive_passes(self):
        self.assertIsNone(verify.not_negative_numeric(candidate=1.3))

    def test_negative_fails(self):
        self.assertRaises(InvalidParameters, verify.not_negative_numeric, candidate=-2.4)


class TestVerifyPositiveNumeric(unittest.TestCase):
    def test_null_int_fails(self):
        self.assertRaises(InvalidParameters, verify.positive_numeric, candidate=0)

    def test_null_float_fails(self):
        self.assertRaises(InvalidParameters, verify.positive_numeric, candidate=0.0)

    def test_positive_passes(self):
        self.assertIsNone(verify.positive_numeric(candidate=1.3))

    def test_negative_fails(self):
        self.assertRaises(InvalidParameters, verify.positive_numeric, candidate=-2.4)


class TestVerifyInteger(unittest.TestCase):
    def test_string_fails(self):
        self.assertRaises(InvalidParameters, verify.integer, candidate="6")

    def test_out_of_bounds_fails(self):
        self.assertRaises(InvalidParameters, verify.integer, candidate=3, minimum=5, maximum=10)

    def test_max_bounds_passes(self):
        self.assertIsNone(verify.integer(candidate=5, minimum=1, maximum=10))

    def test_is_min_bound_passes(self):
        self.assertIsNone(verify.integer(candidate=1, minimum=1, maximum=10))

    def test_is_max_bound_passes(self):
        self.assertIsNone(verify.integer(candidate=10, minimum=1, maximum=10))


class TestVerifyNotNegativeInteger(unittest.TestCase):
    def test_null_int_passes(self):
        self.assertIsNone(verify.not_negative_integer(candidate=0))

    def test_null_float_fails(self):
        self.assertRaises(InvalidParameters, verify.not_negative_integer, candidate=0.0)

    def test_positive_passes(self):
        self.assertIsNone(verify.not_negative_integer(candidate=1))

    def test_negative_fails(self):
        self.assertRaises(InvalidParameters, verify.not_negative_integer, candidate=-2)


class TestVerifyPositiveInteger(unittest.TestCase):
    def test_null_int_fails(self):
        self.assertRaises(InvalidParameters, verify.positive_integer, candidate=0)

    def test_null_float_fails(self):
        self.assertRaises(InvalidParameters, verify.positive_integer, candidate=0.0)

    def test_positive_passes(self):
        self.assertIsNone(verify.positive_integer(candidate=1))

    def test_negative_fails(self):
        self.assertRaises(InvalidParameters, verify.positive_integer, candidate=-2)


class TestVerifyBoolean(unittest.TestCase):
    def test_str_fails(self):
        self.assertRaises(InvalidParameters, verify.boolean, candidate="True")

    def test_none_fails(self):
        self.assertRaises(InvalidParameters, verify.boolean, candidate=None)

    def test_zero_fails(self):
        self.assertRaises(InvalidParameters, verify.boolean, candidate=0)

    def test_one_fails(self):
        self.assertRaises(InvalidParameters, verify.boolean, candidate=1)

    def test_True_passes(self):
        self.assertIsNone(verify.boolean(candidate=True))

    def test_False_passes(self):
        self.assertIsNone(verify.boolean(candidate=False))


class TestVerifyRGBColorTuple(unittest.TestCase):
    def test_list_fails(self):
        self.assertRaises(InvalidParameters, verify.rgb_color_tuple, candidate=[1, 2, 3])

    def test_false_dimensional_tuple_fails(self):
        self.assertRaises(InvalidParameters, verify.rgb_color_tuple, candidate=(0, 1, 2, 3))

    def test_smaller_than_0_fails(self):
        self.assertRaises(InvalidParameters, verify.rgb_color_tuple, candidate=(-0.5, 1, 2))

    def test_bigger_than_255_fails(self):
        self.assertRaises(InvalidParameters, verify.rgb_color_tuple, candidate=(1, 0.2, 275.8))

    def test_float_passes(self):
        self.assertIsNone(verify.rgb_color_tuple(candidate=(100.1, 101.2, 102.3)))

    def test_int_passes(self):
        self.assertIsNone(verify.rgb_color_tuple(candidate=(123, 234, 12)))
