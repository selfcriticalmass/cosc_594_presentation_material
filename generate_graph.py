#!/usr/bin/env python3

import argparse
import json
import random
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate a random directed graph for transitive-closure experiments."
        )
    )
    parser.add_argument(
        "--vertices",
        type=int,
        required=True,
        help="Number of vertices in the graph.",
    )
    parser.add_argument(
        "--density",
        choices=("sparse", "dense"),
        default="sparse",
        help="Choose a sparse or dense graph profile.",
    )
    parser.add_argument(
        "--edge-probability",
        type=float,
        default=None,
        help=(
            "Override the default edge probability with an explicit value in [0, 1]."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible graph generation.",
    )
    parser.add_argument(
        "--acyclic",
        action="store_true",
        help="Restrict edges to go from lower-numbered to higher-numbered vertices.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "edgelist"),
        default="json",
        help="Output format.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path. Defaults to stdout.",
    )
    return parser.parse_args()


def default_edge_probability(vertex_count, density):
    if vertex_count <= 1:
        return 0.0

    if density == "sparse":
        # Keep the expected out-degree near 2 so the graph remains O(n) in size.
        return min(2.0 / (vertex_count - 1), 0.20)

    # Dense graphs should have Theta(n^2) edges, so use a constant probability.
    return 0.45


def validate_args(args):
    if args.vertices < 1:
        raise ValueError("--vertices must be at least 1.")

    if args.edge_probability is not None and not (0.0 <= args.edge_probability <= 1.0):
        raise ValueError("--edge-probability must be between 0 and 1.")


def generate_edges(vertex_count, probability, acyclic, rng):
    edges = []

    for source in range(vertex_count):
        for target in range(vertex_count):
            if source == target:
                continue
            if acyclic and source >= target:
                continue
            if rng.random() < probability:
                edges.append((source, target))

    if vertex_count > 1 and not edges:
        if acyclic:
            edges.append((0, 1))
        else:
            edges.append((0, 1))

    return edges


def build_payload(vertex_count, density, probability, seed, acyclic, edges):
    return {
        "graph_type": "directed",
        "vertices": list(range(vertex_count)),
        "edges": [{"from": source, "to": target} for source, target in edges],
        "metadata": {
            "vertex_count": vertex_count,
            "edge_count": len(edges),
            "density_profile": density,
            "edge_probability": probability,
            "acyclic": acyclic,
            "seed": seed,
        },
    }


def render_edgelist(vertex_count, edges):
    lines = [f"{vertex_count} {len(edges)}"]
    lines.extend(f"{source} {target}" for source, target in edges)
    return "\n".join(lines) + "\n"


def write_output(text, output_path):
    if output_path is None:
        sys.stdout.write(text)
        return

    output_path.write_text(text, encoding="utf-8")


def main():
    args = parse_args()
    validate_args(args)

    rng = random.Random(args.seed)
    probability = (
        args.edge_probability
        if args.edge_probability is not None
        else default_edge_probability(args.vertices, args.density)
    )
    edges = generate_edges(args.vertices, probability, args.acyclic, rng)

    if args.format == "json":
        payload = build_payload(
            args.vertices,
            args.density,
            probability,
            args.seed,
            args.acyclic,
            edges,
        )
        text = json.dumps(payload, indent=2) + "\n"
    else:
        text = render_edgelist(args.vertices, edges)

    write_output(text, args.output)


if __name__ == "__main__":
    main()
