"""Tiny inventory CLI."""

import argparse
import sys

ITEMS = [{"sku": "A1", "name": "Anvil", "qty": 3}, {"sku": "B2", "name": "Bolt", "qty": 120}]


def render(items: list[dict]) -> str:
    return "\n".join(f"{item['sku']}\t{item['name']}\t{item['qty']}" for item in items)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List inventory")
    parser.parse_args(argv)
    sys.stdout.write(render(ITEMS) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
