## Graph Generator

`generate_graph.py` creates random directed graphs for transitive-closure experiments.

Examples:

```bash
python3 generate_graph.py --vertices 12 --density sparse
python3 generate_graph.py --vertices 40 --density dense --format edgelist
python3 generate_graph.py --vertices 20 --density sparse --acyclic --seed 7 --output graph.json
python3 generate_graph.py --vertices 25 --density dense --edge-probability 0.35
```

Arguments:

- `--vertices`: number of vertices.
- `--density sparse|dense`: choose the default sparse or dense profile.
- `--edge-probability`: override the default probability with an explicit value in `[0, 1]`.
- `--seed`: make the output reproducible.
- `--acyclic`: only create edges from lower-numbered vertices to higher-numbered ones.
- `--format json|edgelist`: choose JSON or a simple edge-list format.
- `--output`: write to a file instead of stdout.

Profile defaults:

- `sparse`: uses a probability near `2 / (n - 1)`, so the expected edge count stays linear in `n`.
- `dense`: uses probability `0.45`, so the expected edge count is quadratic in `n`.

The `edgelist` format starts with `n m`, followed by one directed edge `u v` per line.
