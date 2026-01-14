def normalize(values):
    """Normalize a list of numeric values to [0, 1]."""
    min_v = min(values)
    max_v = max(values)
    return [(v - min_v) / (max_v - min_v) for v in values]


def mean(values):
    return sum(values) / len(values)
