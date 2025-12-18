import unittest
from unittest.mock import Mock

from havij.application.services.product_service import ProductService
from havij.domain.model.nutrients import Nutrients
from havij.domain.model.product import Product


class TestProductService(unittest.TestCase):
    def test_lookup_product_returns_product(self) -> None:
        product = Product(
            barcode="123456",
            name="Test Bar",
            nutrients_per_100g=Nutrients(200, 10, 20, 5),
        )
        catalog = Mock()
        catalog.get_by_barcode.return_value = product

        service = ProductService(catalog=catalog)

        result = service.lookup_product("123456")

        self.assertEqual(result, product)
        catalog.get_by_barcode.assert_called_once_with("123456")

    def test_lookup_product_invalid_barcode_raises(self) -> None:
        catalog = Mock()
        service = ProductService(catalog=catalog)

        with self.assertRaises(ValueError):
            service.lookup_product("abc")

        catalog.get_by_barcode.assert_not_called()
