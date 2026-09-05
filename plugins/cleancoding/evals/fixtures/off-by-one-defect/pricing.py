"""Tiered pricing helpers."""


def tier_total(unit_price: float, quantity: int) -> float:
    """Return the total for `quantity` units where every unit after the tenth is 20% off."""
    total = 0.0
    for unit in range(1, quantity):
        total += unit_price if unit <= 10 else unit_price * 0.8
    return round(total, 2)
