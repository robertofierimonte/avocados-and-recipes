import os

import joblib
import numpy as np

from loguru import logger


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute the Root Mean Squared Error (RMSE).

    Args:
        y_true (np.ndarray): (N, ) Array of true targets
        y_pred (np.ndarray): (N, ) Array of model predictions

    Returns:
        float: Value of the Root Mean Squared Error
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute the coefficied of determination (R squared).

    Args:
        y_true (np.ndarray): (N, ) Array of true targets
        y_pred (np.ndarray): (N, ) Array of model predictions

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
        self.W = None
        self.b = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the model on the training data.

        Args:
            X (np.ndarray): (N, p) Training input data
            y (np.ndarray): (N, ) Training target variable
        """
        N, p = X.shape
        X_bias = np.concatenate([np.ones((N, 1)), X], axis=1)
        A = np.linalg.pinv(X_bias) @ y
        self.W = A[1:]
        self.b = A[0]

        # Compute the standard errors and Student's t statistics for each predictor
        yhat = self.predict(X)
        C = np.linalg.inv(X_bias.T @ X_bias)
        sigma_sq = np.sum(np.square(y - yhat)) / (N - p)
        std_errs = np.sqrt((sigma_sq * C).diagonal())
        self.t_scores = A / std_errs

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions for the test data.

        Args:
            X (np.ndarray): (N_t, p) Test input data

        Returns:
            np.ndarray: (N_t, ) Model predictions on the test data
        """
        preds = X @ self.W + self.b
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

    @property
    def coefficients(self) -> np.ndarray:
        """Get the model coefficients.

        Returns:
            np.ndarray: Coefficients associated with the model features. Also includes
                coefficient for the intercept.
        """
        return np.concatenate([self.b[np.newaxis], self.W])
