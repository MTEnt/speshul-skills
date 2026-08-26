#!/usr/bin/env python3
"""Approximate equal-allocation sample sizes for simple two-group tests."""

from __future__ import annotations

import argparse
import json
import math
from statistics import NormalDist


def probability(value: str) -> float:
    parsed = float(value)
    if not 0 < parsed < 1:
        raise argparse.ArgumentTypeError("value must be between 0 and 1")
    return parsed


def positive(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def critical_values(alpha: float, power: float, sides: int, comparisons: int) -> tuple[float, float, float]:
    adjusted_alpha = alpha / comparisons
    tail_alpha = adjusted_alpha / sides
    z_alpha = NormalDist().inv_cdf(1 - tail_alpha)
    z_power = NormalDist().inv_cdf(power)
    return z_alpha, z_power, adjusted_alpha


def proportions(args: argparse.Namespace) -> dict[str, float | int | str]:
    p1 = args.baseline
    p2 = p1 + args.mde
    if not 0 < p2 < 1:
        raise ValueError("baseline + mde must remain between 0 and 1")

    z_alpha, z_power, adjusted_alpha = critical_values(
        args.alpha, args.power, args.sides, args.comparisons
    )
    pooled = (p1 + p2) / 2
    numerator = (
        z_alpha * math.sqrt(2 * pooled * (1 - pooled))
        + z_power * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2
    raw_per_group = numerator / (p2 - p1) ** 2
    adjusted_per_group = raw_per_group * args.design_effect / (1 - args.attrition)
    per_group = math.ceil(adjusted_per_group)
    return {
        "method": "two_proportions_normal_approximation",
        "baseline": p1,
        "alternative": p2,
        "absolute_mde": args.mde,
        "relative_mde": args.mde / p1,
        "alpha": args.alpha,
        "adjusted_alpha": adjusted_alpha,
        "power": args.power,
        "sides": args.sides,
        "comparisons": args.comparisons,
        "design_effect": args.design_effect,
        "attrition": args.attrition,
        "per_group": per_group,
        "total": per_group * 2,
    }


def means(args: argparse.Namespace) -> dict[str, float | int | str]:
    z_alpha, z_power, adjusted_alpha = critical_values(
        args.alpha, args.power, args.sides, args.comparisons
    )
    raw_per_group = 2 * ((z_alpha + z_power) * args.stddev / args.mde) ** 2
    adjusted_per_group = raw_per_group * args.design_effect / (1 - args.attrition)
    per_group = math.ceil(adjusted_per_group)
    return {
        "method": "two_independent_means_normal_approximation",
        "stddev": args.stddev,
        "absolute_mde": args.mde,
        "standardized_mde": args.mde / args.stddev,
        "alpha": args.alpha,
        "adjusted_alpha": adjusted_alpha,
        "power": args.power,
        "sides": args.sides,
        "comparisons": args.comparisons,
        "design_effect": args.design_effect,
        "attrition": args.attrition,
        "per_group": per_group,
        "total": per_group * 2,
    }


def add_shared_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mde", required=True, type=positive, help="absolute minimum detectable effect")
    parser.add_argument("--alpha", type=probability, default=0.05)
    parser.add_argument("--power", type=probability, default=0.80)
    parser.add_argument("--sides", type=int, choices=(1, 2), default=2)
    parser.add_argument("--comparisons", type=int, default=1)
    parser.add_argument("--design-effect", type=positive, default=1.0)
    parser.add_argument("--attrition", type=float, default=0.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="metric", required=True)

    proportion_parser = subparsers.add_parser("proportions")
    proportion_parser.add_argument("--baseline", required=True, type=probability)
    add_shared_arguments(proportion_parser)

    means_parser = subparsers.add_parser("means")
    means_parser.add_argument("--stddev", required=True, type=positive)
    add_shared_arguments(means_parser)

    args = parser.parse_args()
    if args.comparisons < 1:
        parser.error("--comparisons must be at least 1")
    if not 0 <= args.attrition < 1:
        parser.error("--attrition must be at least 0 and less than 1")
    return args


def main() -> int:
    args = parse_args()
    try:
        result = proportions(args) if args.metric == "proportions" else means(args)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
