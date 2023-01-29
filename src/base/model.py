import os

import joblib
import numpy as np

from loguru import logger


def rmse(y_true: np.array, y_pred: np.array) -> float:
    """Compute the Root Mean Squared Error (RMSE).

    Args:
        y_true (np.array): (N, ) Array of true targets
        y_pred (np.array): (N, ) Array of model predictions

    Returns:
        float: Value of the Root Mean Squared Error
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def r2(y_true: np.array, y_pred: np.array) -> float:
    """Compute the coefficied of determination (R squared).

    Args:
        y_true (np.array): (N, ) Array of true targets
        y_pred (np.array): (N, ) Array of model predictions

    Returns:
        float: Value of the R squared
    """
    sse = np.sum((y_true - y_pred) ** 2)  # Sum of Squared Errors
    ssr = np.sum((np.mean(y_true) - y_pred) ** 2)  # Sum of Squared Residuals
    return ssr / (ssr + sse)  # R squared


class LinearRegression:
    """A Linear Regression model implemented in Numpy."""

    def __init__(self) -> None:
        """Initialise the object."""
        self._W = None
        self._b = None
        self._res = None

    def fit(self, X: np.array, y: np.array) -> None:
        """Fit the model on the training data.

        Args:
            X (np.array): (N, p) Training input data
            y (np.array): (N, ) Training target variable
        """
        # Get the number of training samples
        N, _ = X.shape
        # Add the bias
        X_bias = np.concatenate([np.ones((N, 1)), X], axis=1)
        logger.debug(f"X_b shape: {X_bias.shape} .")
        # Compute the LR coefficients
        A = np.linalg.pinv(X_bias) @ y
        logger.debug(f"A shape: {A.shape} .")
        self._W = A[1:]
        self._b = A[0]
        # Compute the residuals
        y_pred = X_bias @ A
        sse = np.sum((y - y_pred) ** 2)

    def predict(self, X: np.array) -> np.array:
        """Generate predictions for the test data.

        Args:
            X (np.array): (N_t, p) Test input data

        Returns:
            np.array: (N_t, ) Model predictions on the test data
        """
        preds = X @ self._W + self._b
        logger.debug(f"Preds shape: {preds.shape} .")
        return preds

    @staticmethod
    def load_model(file_name: os.PathLike):
        """Load the pre-trained model from a source.

        Args:
            file_name (os.PathLike): Path from where the model will be loaded.

        Returns:
            The pre-trained model.
        """
        model = joblib.load(file_name)
        logger.info(f"Loaded model from {file_name} .")
        return model

    def save_model(self, file_name: os.PathLike) -> None:
        """Save the pre-trained model to a target.

        Args:
            file_name (os.PathLike): Path where the model will be saved to.
        """
        directory = os.path.dirname(file_name)
        logger.debug(f"Model directory: {directory} .")
        os.makedirs(directory, exist_ok=True)
        joblib.dump(self, file_name)
        logger.info(f"Saved model to {file_name} .")

    def feature_importance(self):
        pass
