#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int vertex_count;
    int edge_count;
    int *head;
    int *to;
    int *next;
} Graph;

typedef struct {
    int matrix;
    int reflexive;
    const char *input_path;
} Options;

static void usage(const char *program_name) {
    fprintf(
        stderr,
        "Usage: %s [--matrix] [--reflexive] [graph.edgelist]\n"
        "Reads an edge-list graph and prints its serial transitive closure.\n",
        program_name
    );
}

static int parse_args(int argc, char **argv, Options *options) {
    int i;

    options->matrix = 0;
    options->reflexive = 0;
    options->input_path = NULL;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--matrix") == 0) {
            options->matrix = 1;
        } else if (strcmp(argv[i], "--reflexive") == 0) {
            options->reflexive = 1;
        } else if (
            strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0
        ) {
            usage(argv[0]);
            return 1;
        } else if (argv[i][0] == '-') {
            fprintf(stderr, "Unknown option: %s\n", argv[i]);
            usage(argv[0]);
            return 0;
        } else if (options->input_path != NULL) {
            fprintf(stderr, "Only one input file may be provided.\n");
            usage(argv[0]);
            return 0;
        } else {
            options->input_path = argv[i];
        }
    }

    return 2;
}

static void free_graph(Graph *graph) {
    free(graph->head);
    free(graph->to);
    free(graph->next);
    graph->head = NULL;
    graph->to = NULL;
    graph->next = NULL;
}

static int read_graph(FILE *input, Graph *graph) {
    int vertex_count;
    int edge_count;
    int edge_index;

    if (fscanf(input, "%d %d", &vertex_count, &edge_count) != 2) {
        fprintf(stderr, "Failed to read the graph header.\n");
        return 0;
    }

    if (vertex_count < 1 || edge_count < 0) {
        fprintf(stderr, "Graph header must satisfy n >= 1 and m >= 0.\n");
        return 0;
    }

    graph->vertex_count = vertex_count;
    graph->edge_count = edge_count;
    graph->head = malloc((size_t)vertex_count * sizeof(*graph->head));
    graph->to = malloc((size_t)edge_count * sizeof(*graph->to));
    graph->next = malloc((size_t)edge_count * sizeof(*graph->next));

    if (graph->head == NULL || graph->to == NULL || graph->next == NULL) {
        fprintf(stderr, "Out of memory while reading the graph.\n");
        free_graph(graph);
        return 0;
    }

    for (edge_index = 0; edge_index < vertex_count; ++edge_index) {
        graph->head[edge_index] = -1;
    }

    for (edge_index = 0; edge_index < edge_count; ++edge_index) {
        int source;
        int target;

        if (fscanf(input, "%d %d", &source, &target) != 2) {
            fprintf(stderr, "Failed to read edge %d.\n", edge_index);
            free_graph(graph);
            return 0;
        }

        if (source < 0 || source >= vertex_count || target < 0 || target >= vertex_count) {
            fprintf(
                stderr,
                "Edge %d has endpoint outside [0, %d).\n",
                edge_index,
                vertex_count
            );
            free_graph(graph);
            return 0;
        }

        graph->to[edge_index] = target;
        graph->next[edge_index] = graph->head[source];
        graph->head[source] = edge_index;
    }

    return 1;
}

static unsigned char *compute_transitive_closure(
    const Graph *graph,
    int reflexive,
    size_t *closure_edge_count
) {
    int source;
    int vertex_count = graph->vertex_count;
    int *queue = malloc((size_t)vertex_count * sizeof(*queue));
    int *seen = calloc((size_t)vertex_count, sizeof(*seen));
    unsigned char *closure = calloc(
        (size_t)vertex_count * (size_t)vertex_count,
        sizeof(*closure)
    );
    int visit_mark = 0;

    if (queue == NULL || seen == NULL || closure == NULL) {
        fprintf(stderr, "Out of memory while computing the closure.\n");
        free(queue);
        free(seen);
        free(closure);
        return NULL;
    }

    *closure_edge_count = 0;

    for (source = 0; source < vertex_count; ++source) {
        int front = 0;
        int back = 0;

        ++visit_mark;
        if (visit_mark == 0) {
            memset(seen, 0, (size_t)vertex_count * sizeof(*seen));
            visit_mark = 1;
        }

        seen[source] = visit_mark;
        queue[back++] = source;

        if (reflexive) {
            closure[(size_t)source * (size_t)vertex_count + (size_t)source] = 1;
            *closure_edge_count += 1;
        }

        while (front < back) {
            int current = queue[front++];
            int edge;

            for (edge = graph->head[current]; edge != -1; edge = graph->next[edge]) {
                int target = graph->to[edge];
                size_t offset = (size_t)source * (size_t)vertex_count + (size_t)target;

                if (seen[target] == visit_mark) {
                    continue;
                }

                seen[target] = visit_mark;
                queue[back++] = target;

                if (closure[offset] == 0) {
                    closure[offset] = 1;
                    *closure_edge_count += 1;
                }
            }
        }
    }

    free(queue);
    free(seen);
    return closure;
}

static void write_edgelist(
    const unsigned char *closure,
    int vertex_count,
    size_t closure_edge_count
) {
    int source;
    int target;

    printf("%d %zu\n", vertex_count, closure_edge_count);
    for (source = 0; source < vertex_count; ++source) {
        for (target = 0; target < vertex_count; ++target) {
            if (closure[(size_t)source * (size_t)vertex_count + (size_t)target] != 0) {
                printf("%d %d\n", source, target);
            }
        }
    }
}

static void write_matrix(const unsigned char *closure, int vertex_count) {
    int source;
    int target;

    printf("%d\n", vertex_count);
    for (source = 0; source < vertex_count; ++source) {
        for (target = 0; target < vertex_count; ++target) {
            if (target > 0) {
                putchar(' ');
            }
            printf(
                "%u",
                (unsigned int)closure[
                    (size_t)source * (size_t)vertex_count + (size_t)target
                ]
            );
        }
        putchar('\n');
    }
}

int main(int argc, char **argv) {
    Options options;
    Graph graph = {0};
    FILE *input = stdin;
    unsigned char *closure;
    size_t closure_edge_count = 0;
    int parse_result = parse_args(argc, argv, &options);

    if (parse_result == 1) {
        return EXIT_SUCCESS;
    }

    if (parse_result == 0) {
        return EXIT_FAILURE;
    }

    if (options.input_path != NULL) {
        input = fopen(options.input_path, "r");
        if (input == NULL) {
            fprintf(
                stderr,
                "Failed to open %s: %s\n",
                options.input_path,
                strerror(errno)
            );
            return EXIT_FAILURE;
        }
    }

    if (!read_graph(input, &graph)) {
        if (input != stdin) {
            fclose(input);
        }
        return EXIT_FAILURE;
    }

    if (input != stdin) {
        fclose(input);
    }

    closure = compute_transitive_closure(
        &graph,
        options.reflexive,
        &closure_edge_count
    );
    if (closure == NULL) {
        free_graph(&graph);
        return EXIT_FAILURE;
    }

    if (options.matrix) {
        write_matrix(closure, graph.vertex_count);
    } else {
        write_edgelist(closure, graph.vertex_count, closure_edge_count);
    }

    free(closure);
    free_graph(&graph);
    return EXIT_SUCCESS;
}
