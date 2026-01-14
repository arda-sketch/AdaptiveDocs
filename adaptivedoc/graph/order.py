import networkx as nx


def topological_order(graph: nx.DiGraph):
    """
    Возвращает порядок генерации:
    от листьев (зависимостей) к корням.
    """
    try:
        return list(nx.topological_sort(graph))
    except nx.NetworkXUnfeasible:
        # fallback: если цикл (редко, но возможно)
        return list(graph.nodes)
