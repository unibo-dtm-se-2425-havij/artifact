from __future__ import annotations

MAX_GRAMS = 3000.0


def validate_grams(grams: float) -> None:
    if grams <= 0:
        raise ValueError("grams must be > 0")
    if grams > MAX_GRAMS:
        raise ValueError(f"grams must be <= {MAX_GRAMS:.0f}")


def validate_product_name(product_name: str) -> None:
    if not product_name.strip():
        raise ValueError("product name must be non-empty")


def validate_barcode(barcode: str) -> None:
    b = barcode.strip()
    if not b:
        raise ValueError("barcode must be non-empty")
    if not b.isdigit():
        # OpenFoodFacts barcodes are numeric (EAN/UPC). Keep validation simple.
        raise ValueError("barcode must contain only digits")


def validate_macros_per_100g(
    protein_g: float,
    carbs_g: float,
    fat_g: float,
) -> None:
    for label, value in (("protein", protein_g), ("carbs", carbs_g), ("fat", fat_g)):
        if value < 0:
            raise ValueError(f"{label} must be >= 0")
        if value > 100:
            raise ValueError(f"{label} must be <= 100")
    if protein_g + carbs_g + fat_g > 100:
        raise ValueError("protein + carbs + fat must be <= 100")
