import copy
import numpy as np
from .utils import get_matrix_in_format
from scipy.sparse import issparse, csr_matrix

class MLClassifierBase(object):
    """Base class providing API and common functions for all multi-label classifiers.
 
    Parameters
    ----------

    classifier : scikit classifier type
        The base classifier that will be used in a class, will be automagically put under self.classifier for future access.
    require_dense : boolean
        Whether the base classifier requires input as dense arrays, False by default
    """
    def __init__(self, classifier = None, require_dense = False):
        
        super(MLClassifierBase, self).__init__()
        self.classifier = classifier
        self.require_dense = require_dense


    def generate_data_subset(self, y, subset, axis):
        """This function subsets the array of binary label vectors to include only certain labels. 

        Parameters
        ----------

        y : array-like of array-likes
            An array-like of binary label vectors.
        
        subset: array-like of integers
            array of integers, indices that will be subsetted from array-likes in y

        axis: integer 0 for 'rows', 1 for 'labels', 
            control variable for whether to return rows or labels as indexed by subset

        Returns
        -------

        multi-label binary label vector : array-like of array-likes of {0,1}
            array of binary label vectors including label data only for labels from parameter labels
        """
        return_data = None
        if axis == 1:
            return_data = y.tocsc()[:, subset]
        elif axis == 0:
            return_data = y.tocsr()[subset, :]

        return return_data

    def ensure_1d(self, y):
        return [t[0,0] for t in y.todense()]


    def fit(self, X, y):
        """Abstract class to implement to fit classifier according to X,y.

        Parameters
        ----------
        
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and n_features is the number of features.

        y : array-like, shape = [n_samples, n_labels]
            Binary label vectors with 1 if label should be applied and 0 if not.

        Returns
        -------
        self : object
            Returns self.
        """
        raise NotImplementedError("MLClassifierBase::fit()")

    def predict(self, X):
        """Abstract class to implement to perform classification on an array of test vectors X.

        Parameters
        ----------
        
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and n_features is the number of features.

        Returns
        -------

        y : array-like, shape = [n_samples, n_labels]
            Binary label vectors with 1 if label should be applied and 0 if not. n_labels is number of labels in the 
            multi-label instance that the classifier was fit to.

        """
        raise NotImplementedError("MLClassifierBase::predict()")

    def get_params(self, deep=True):
        """
        Introspection of classifier for search models like cross validation and grid
        search.
        Parameters
        ----------
        deep : boolean
            If true all params will be introspected also and appended to the output dict.
        Returns
        -------
        out : dictionary
            Dictionary of all parameters and their values. If deep=True the dictionary
            also holds the parameters of the parameters.
        """
        out = dict()

        out["classifier"] = self.classifier
        out["require_dense"] = self.require_dense

        # deep introspection of estimator parameters
        if deep and hasattr(self.classifier, 'get_params'):
            deep_items = value.get_params().items()
            out.update((key + '__' + k, val) for k, val in deep_items)

        return out

    def set_params(self, **parameters):
        """
        Set parameters as returned by `get_params`.
        @see https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/base.py#L243
        """

        if not parameters:
            return self

        for parameter, value in parameters.items():
            self.setattr(parameter, value)

        return self
    


class RepeatClassifier(MLClassifierBase):

    def __init__(self, value_to_repeat = None):
        
        super(RepeatClassifier, self).__init__()

    def fit(self, X, y):
        self.value_to_repeat = copy.copy(y.tocsr[0,:])
        self.return_value = np.full(y)
        return self

    def predict(self, X):
        return np.array([np.copy(self.value_to_repeat) for x in xrange(len(X))])

