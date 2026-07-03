# Model Classes

from scipy.optimize import curve_fit
import numpy as np


class LogLogistic5p:
    """
    Instantiate class with x and y arrays
    Fit a 5 parameter log logistic curve
    """

    def __init__(self, x: np.array, y: np.array):
        self.x = x  # independent variates
        self.y = y  # dependent variates
        self.params = np.array([])  # log-logistic 5 parameters (b, c, d, e, f)
        self.fitted = np.array([])  # fitted values of the dependent variable
        self.pcov = np.array([])  # covariance matrix of curve parameters. variance of parameters on diagonal
        self.perr = np.array([])  # variance of parameter estimates

    @staticmethod
    def _ll5p(x, b, c, d, e, f):
        """
        Fits a 5 parameter log logistic curve to a data point
        :param x: the x parameter data to be fit, in this case the time in seconds
        :param b: reserved for internal use in scipy.optimize.curve_fit()
        :param c: reserved for internal use in scipy.optimize.curve_fit()
        :param d: reserved for internal use in scipy.optimize.curve_fit()
        :param e: reserved for internal use in scipy.optimize.curve_fit()
        :param f: reserved for internal use in scipy.optimize.curve_fit()
        :return: a fitted value
        """
        return c + (d - c) / (1 + np.exp(b * (np.log(x) - np.log(e)))) ** f

    def fit(self, verbose=False):
        try:
            self.params, self.pcov = curve_fit(self._ll5p, self.x, self.y)
            self.perr = np.sqrt(np.diag(self.pcov))
            self.fitted = self._ll5p(self.x, *self.params)
            if verbose:
                print(f"Fitted parameters: {np.round(self.params, 3)}")
        except TypeError as e:
            print("\nPlease refit the curve using more data points.")
            self.params = np.array([])
            self.pcov = np.array([])
            self.perr = np.array([])
            self.fitted = np.array([])
            raise e

    def predict(self, new_obs) -> np.array:
        """
        predict a y values for an array of new x observations
        :return: array of length = new_obs
        """
        try:
            assert len(self.params) == 5, "Error: curve parameters are missing."
            return self._ll5p(new_obs, *self.params)
        except AssertionError as e:
            print("\nPlease fit curve before predicting new data points.")
            raise e


x_val = np.array([2, 4, 6, 7, 8, 9, 10, 12, 14, 16])
y_val = np.array([90, 90, 87, 65, 42, 25, 20, 15, 14, 14])
new_x = np.array([2.5, 4.6, 6.1, 7.9, 8.3, 20])

curve = LogLogistic5p(x_val, y_val)
curve.fit()

print(curve.predict(new_x))

