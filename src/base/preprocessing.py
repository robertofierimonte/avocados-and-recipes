from typing import Optional, Union

import numpy as np
import pandas as pd
from numba import jit


def get_previous_price():
    pass


@jit(cache=True, nopython=True)
def sin_transformer(arr: np.ndarray, period: float) -> np.ndarray:
    """Transform the input into a sine function.

    Args:
        arr (np.ndarray): (N, ) Values for the circular feature
        period (float): Periodicity of the sine function

    Returns:
        np.ndarray: (N, ) Transformed inputs
    """
    return np.sin(arr / period * 2 * np.pi)


@jit(cache=True, nopython=True)
def cos_transformer(arr: np.ndarray, period: float) -> np.ndarray:
    """Transform the input into a cosine function.

    Args:
        arr (np.ndarray): (N, ) Values for the circular feature
        period (float): Periodicity of the cosine function

    Returns:
        np.ndarray: Transformed inputs
    """
    return np.cos(arr / period * 2 * np.pi)


@jit(cache=True, nopython=True)
def _base_distances(arr: np.ndarray, base: float) -> np.ndarray:
    """Calculate the distances between all array values and a single base.

    0 and 1 are assumed to be at the same position.

    Args:
        arr (np.ndarray): (N, ) Scaled input data
        base (float): Base of the RBF

    Returns:
        np.ndarray: (N, ) Distances between each element of `arr` and `base`
    """
    abs_diff_0 = np.abs(arr - base)
    abs_diff_1 = 1 - np.abs(arr - base)
    return np.minimum(abs_diff_0, abs_diff_1)


@jit(cache=True, nopython=True, parallel=True)
def _array_bases_distances(arr: np.ndarray, bases: np.ndarray) -> np.ndarray:
    """Calculate the distances between all arrays and bases values.

    Args:
        arr (np.ndarray): (N, ) Scaled input data
        bases (np.ndarray): (n_periods, ) Bases of the RBF

    Returns:
        np.ndarray: (N, n_periods) Distances between each element of
            `arr` and each base
    """
    res = np.empty((arr.shape[0], bases.shape[0]), dtype=np.float)

    for e, b in enumerate(bases):
        res[:, e] = _base_distances(arr, b)

    return res


class RepeatingRadialBasisFunction:
    """Transformer for features that have some form of circularity.

    This is a transformer for features with some form of circularity.
    E.g. for days of the week you might face the problem that, conceptually,
    day 7 is as close to day 6 as it is to day 1. While numerically their
    distance is different. This transformer remedies that problem.

    The transformer selects a column and transforms it with a given number of
    repeating (radial) basis functions. Radial basis functions are bell-curve
    shaped functions which take the original data as input. The basis functions
    are equally spaced over the input range. The key feature of repeating basis
    functions is that they are continuous when moving from the max to the min
    of the input range. As a result these repeating basis functions can capture
    how close each datapoint is to the center of each repeating basis function,
    even when the input data has a circular nature.

    Adapted from: https://scikit-lego.netlify.app/_modules/sklego/preprocessing/repeatingbasis.html#RepeatingBasisFunction
    """

    def __init__(
        self, n_periods: int, input_range: Optional[tuple] = None, width: float = 1.0
    ) -> None:
        """Initialise the transformer.

        Args:
            n_periods (int): Number of basis functions to create, i.e., the
                number of columns that will exit the transformer
            input_range (tuple, optional): the values at which the data repeats
                itself. For example, for days of the week this is (1,7). If not
                provided it is inferred from the training data.
                Defaults to None
            width (float, optional): Width of the radial basis functions.
                Defaults to 1
        """
        self.n_periods = n_periods
        self.input_range = input_range
        self.width = width

    def fit(self, X: Union[pd.Series, np.ndarray]) -> None:
        """Fit the transformer over an input column.

        Args:
            X (Union[pd.Series, np.ndarray]): (N, ) Values for the
            circular feature.
        """
        # If X is an array, ensure it has only one dimension
        if isinstance(X, np.ndarray):
            assert len(X.shape) == 1

        # Find the minimum and maximum values for standardisation if not
        # given explicitely
        if self.input_range is None:
            self.input_range = (X.min(), X.max())

        # Define the bases as linearly spaced values. Exclude the last value
        # because it is idenfical to the first one for the repeating basis
        # function
        self._bases = np.linspace(0, 1, self.n_periods + 1)[:-1]

        # The curves should be narrower (wider) when there are more (fewer)
        # periods
        self.width /= self.n_periods

    def transform(self, X: Union[pd.Series, np.ndarray]) -> np.array:
        """Transform the inputs by applying the Repeating RBFs.

        Args:
            X (Union[pd.Series, np.ndarray]): (N, ) Values for the circular
                feature

        Returns:
            np.array: (N, self.n_periods) Transformed input values
        """
        # If X is an Numpy array, ensure it has only one dimension
        if isinstance(X, np.ndarray):
            assert len(X.shape) == 1
            X_copy = X.copy()
        else:
            X_copy = X.values.copy()

        # MinMax Scale to 0-1
        X_copy = X_copy - self.input_range[0]
        X_copy = X_copy / (self.input_range[1] - self.input_range[0])

        # Calculate the distances of the input data from the bases
        base_distances = _array_bases_distances(X_copy, self._bases)

        # Create and return the Gaussian RBFs
        return np.exp(-((base_distances / self.width) ** 2))
