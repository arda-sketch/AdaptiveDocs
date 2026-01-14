from utils.helpers import mean
from services.math_service import square


def variance(values):
    avg = mean(values)
    return sum((v - avg) ** 2 for v in values) / len(values)


def rms(values):
    return mean([square(v) for v in values]) ** 0.5
