import unittest

from havij.domain.model.nutrients import Nutrients


class TestNutrients(unittest.TestCase):
    def test_nutrients_add_and_scale(self) -> None:
        n = Nutrients(kcal=100, protein_g=10, carbs_g=20, fat_g=5)
        m = Nutrients(kcal=50, protein_g=2, carbs_g=1, fat_g=0)
        s = n + m
        self.assertEqual(s.kcal, 150)
        self.assertEqual(s.protein_g, 12)
        self.assertEqual(s.carbs_g, 21)
        self.assertEqual(s.fat_g, 5)

        t = n.scale(0.5)
        self.assertEqual(t.kcal, 50)
        self.assertEqual(t.protein_g, 5)
