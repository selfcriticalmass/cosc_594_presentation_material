from manim import *


class SparseSequentialTC(Scene):
    def construct(self):
        node_fill = "#1F2937"
        edge_base = GREY_B
        edge_seen = BLUE_D
        source_color = GOLD_D
        active_color = YELLOW
        discovered_color = GREEN_D
        processed_color = BLUE_E

        vertices = ["A", "B", "C", "D", "E", "F"]
        edges = [
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("C", "D"),
            ("C", "E"),
            ("D", "F"),
            ("E", "F"),
        ]

        adjacency = {v: [] for v in vertices}
        for u, v in edges:
            adjacency[u].append(v)

        layout = {
            "A": LEFT * 4.8 + UP * 1.5,
            "B": LEFT * 3.1 + UP * 2.5,
            "C": LEFT * 3.0 + UP * 0.4,
            "D": LEFT * 1.1 + UP * 1.5,
            "E": LEFT * 1.0 + DOWN * 0.6,
            "F": RIGHT * 1.0 + UP * 0.5,
        }

        labels = {v: Text(v, font_size=26, weight=BOLD) for v in vertices}
        graph = DiGraph(
            vertices,
            edges,
            layout=layout,
            labels=labels,
            vertex_config={
                "radius": 0.30,
                "fill_color": node_fill,
                "fill_opacity": 1.0,
                "stroke_color": WHITE,
                "stroke_width": 2,
            },
            edge_config={
                "stroke_color": edge_base,
                "stroke_width": 3,
                "tip_length": 0.18,
            },
        ).shift(DOWN * 0.2)

        title = Text(
            "Sequential Transitive Closure on a Sparse Graph",
            font_size=34,
            weight=BOLD,
        )
        subtitle = Text(
            "Run a search from each source; add (s, v) when v is first reached",
            font_size=22,
        )
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.14).to_edge(UP)

        status_box = RoundedRectangle(
            width=6.8,
            height=2.2,
            corner_radius=0.16,
            stroke_color=BLUE_E,
        ).to_corner(DL).shift(RIGHT * 0.55 + UP * 0.35)

        closure_box = RoundedRectangle(
            width=4.6,
            height=6.0,
            corner_radius=0.16,
            stroke_color=GREEN_E,
        ).to_edge(RIGHT).shift(DOWN * 0.15)

        closure_title = Text("Closure Pairs", font_size=28, weight=BOLD)
        closure_title.move_to(closure_box.get_top() + DOWN * 0.35)

        closure_note = Text(
            "(positive-length reachability)",
            font_size=18,
            slant=ITALIC,
        ).next_to(closure_title, DOWN, buff=0.10)

        count_label = Text("Pairs:", font_size=24)
        pair_count = Text("0", font_size=24, color=GREEN_C)
        count_group = VGroup(count_label, pair_count).arrange(RIGHT, buff=0.15)
        count_group.next_to(closure_note, DOWN, buff=0.18)
        count_group.align_to(closure_title, LEFT)

        def make_status(source, queue, seen, active):
            ordered_seen = [v for v in vertices if v in seen]
            queue_text = "[" + ", ".join(queue) + "]" if queue else "[]"
            seen_text = "{" + ", ".join(ordered_seen) + "}" if ordered_seen else "{}"

            line1 = Text(f"Source: {source}", font_size=26, weight=BOLD)
            line2 = Text(f"Queue: {queue_text}", font_size=22)
            line3 = Text(f"Reached: {seen_text}", font_size=22)
            line4 = Text(f"Expanding: {active}", font_size=22)

            group = VGroup(line1, line2, line3, line4).arrange(
                DOWN,
                aligned_edge=LEFT,
                buff=0.10,
            )
            group.move_to(status_box.get_center())
            group.align_to(status_box, LEFT).shift(RIGHT * 0.25)
            return group

        def make_pair_row(index, source, target):
            row = Text(f"{source} -> {target}", font_size=23, color=GREEN_C)
            row.move_to(closure_box.get_top() + DOWN * (1.55 + 0.34 * index))
            row.align_to(closure_box, LEFT)
            row.shift(RIGHT * 0.30)
            return row

        status_display = make_status("-", [], set(), "-")
        closure_rows = VGroup()

        self.play(FadeIn(header, shift=DOWN * 0.2))
        self.play(Create(graph), run_time=1.3)
        self.play(
            Create(status_box),
            Create(closure_box),
            FadeIn(status_display),
            FadeIn(closure_title),
            FadeIn(closure_note),
            FadeIn(count_group),
        )

        for source in vertices:
            self.play(
                *[
                    graph.vertices[v].animate.set_fill(node_fill).set_stroke(
                        color=WHITE,
                        width=2,
                    )
                    for v in vertices
                ],
                *[
                    graph.edges[e].animate.set_stroke(
                        color=edge_base,
                        width=3,
                    )
                    for e in edges
                ],
                Transform(status_display, make_status(source, [source], {source}, "-")),
                run_time=0.5,
            )

            queue = [source]
            seen = {source}

            self.play(
                graph.vertices[source].animate.set_fill(source_color),
                run_time=0.3,
            )

            while queue:
                u = queue.pop(0)

                self.play(
                    Transform(status_display, make_status(source, queue, seen, u)),
                    graph.vertices[u].animate.set_fill(active_color),
                    run_time=0.3,
                )
                self.play(Indicate(graph.vertices[u], color=active_color), run_time=0.35)

                for v in adjacency[u]:
                    edge = graph.edges[(u, v)]

                    self.play(
                        edge.animate.set_stroke(color=active_color, width=5),
                        run_time=0.22,
                    )

                    if v not in seen:
                        seen.add(v)
                        queue.append(v)

                        new_row = make_pair_row(len(closure_rows), source, v)
                        closure_rows.add(new_row)

                        self.play(
                            graph.vertices[v].animate.set_fill(discovered_color),
                            FadeIn(new_row, shift=RIGHT * 0.15),
                            Transform(
                                pair_count,
                                Text(
                                    str(len(closure_rows)),
                                    font_size=24,
                                    color=GREEN_C,
                                ).move_to(pair_count)
                            ),
                            Transform(
                                status_display,
                                make_status(source, queue, seen, u),
                            ),
                            run_time=0.48,
                        )
                    else:
                        self.play(
                            Indicate(graph.vertices[v], color=MAROON_B, scale_factor=1.05),
                            run_time=0.25,
                        )

                    self.play(
                        edge.animate.set_stroke(color=edge_seen, width=3),
                        run_time=0.18,
                    )

                final_color = source_color if u == source else processed_color
                self.play(
                    graph.vertices[u].animate.set_fill(final_color),
                    run_time=0.2,
                )

            self.play(
                Transform(status_display, make_status(source, [], seen, "done")),
                run_time=0.25,
            )
            self.wait(0.25)

        self.wait(1.5)
