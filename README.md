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

## Serial Transitive Closure in C

`serial_tc.c` computes a serial transitive closure by running a graph search from
each source vertex. It reads the same edge-list format that
`generate_graph.py --format edgelist` produces.

Build it with:

```bash
make
```

Run it on a generated graph:

```bash
python3 generate_graph.py --vertices 12 --density sparse --seed 7 --format edgelist | ./serial_tc
python3 generate_graph.py --vertices 12 --density sparse --seed 7 --format edgelist | ./serial_tc --matrix
./serial_tc graphs/sparse_6_seed7.edgelist
./serial_tc --reflexive graphs/sparse_acyclic_8_seed11.edgelist
```

Notes:

- Default output is an edge-list closure: first `n m_tc`, then one reachable pair
  `u v` per line.
- `--matrix` prints an `n x n` reachability matrix instead.
- By default the program matches the positive-length reachability used in the
  slide code, so it does not add `(v, v)` automatically.
- `--reflexive` adds every `(v, v)` pair to produce the reflexive transitive
  closure.

Sample generated inputs are checked into `graphs/` for quick experiments.
