import unittest
from unittest.mock import patch

from havij.infrastructure.api.openfoodfacts_client import OpenFoodFactsClient


class FakeResp:
    def __init__(self, status_code: int, json_data):
        self.status_code = status_code
        self._json = json_data
        self.text = "x"

    def json(self):
        return self._json


class TestOpenFoodFactsClient(unittest.TestCase):
    def test_openfoodfacts_client_parses_minimal(self) -> None:
        client = OpenFoodFactsClient()

        def fake_get(url, timeout):
            return FakeResp(200, {
                "product": {
                    "product_name": "Test Product",
                    "nutriments": {
                        "energy-kcal_100g": 200,
                        "proteins_100g": 10,
                        "carbohydrates_100g": 20,
                        "fat_100g": 5
                    }
                }
            })

        with patch.object(client._session, "get", fake_get):
            p = client.get_product_by_barcode("123456")
        self.assertEqual(p.name, "Test Product")
        self.assertEqual(p.nutrients_per_100g.kcal, 200)
        self.assertEqual(p.nutrients_for_grams(50).kcal, 100)
