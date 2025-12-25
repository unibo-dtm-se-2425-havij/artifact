from __future__ import annotations

def validate_grams(grams: float) -> None:
    if grams <= 0:
        raise ValueError("grams must be > 0")


def validate_barcode(barcode: str) -> None:
    b = barcode.strip()
    if not b:
        raise ValueError("barcode must be non-empty")
    if not b.isdigit():
        # OpenFoodFacts barcodes are numeric (EAN/UPC). Keep validation simple.
        raise ValueError("barcode must contain only digits")


def validate_macros_under_grams(
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    grams: float,
) -> None:
    if protein_g + carbs_g + fat_g >= grams:
        raise ValueError("protein + carbs + fat must be < grams")
