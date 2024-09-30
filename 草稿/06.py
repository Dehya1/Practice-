import numpy as np


def sample(total, constraints):
    constraints_sum = sum(constraints)
    if total > constraints_sum:
        pass
    else:
        probabilities = np.array(list(constraints)) / constraints_sum
        rng = np.random.default_rng()
        samples = rng.multinomial(total, probabilities, size=1)
        return samples
    # return next(val for val in samples if np.all(val < constraints))

r1 = [20, 50]

df = sample(60, r1)
print(df)
print(df.sum())