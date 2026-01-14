from services.stats_service import variance, rms


def analyze(values):
    v = variance(values)
    r = rms(values)
    return {
        "variance": v,
        "rms": r,
    }


if __name__ == "__main__":
    data = [1, 2, 3, 4, 5]
    print(analyze(data))
