
from __future__ import division
import numpy as np
import scipy.sparse as sp
from itertools import product

from sklearn.externals.six.moves import xrange
from sklearn.externals.six import iteritems

from scipy.sparse import issparse
from scipy.sparse import csc_matrix
from scipy.sparse import csr_matrix
from scipy.sparse import coo_matrix
from scipy.sparse import dok_matrix
from scipy.sparse import lil_matrix

from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_true
from sklearn.utils.testing import assert_false
from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_raises_regex

from sklearn.utils.multiclass import unique_labels
from sklearn.utils.multiclass import is_multilabel
from sklearn.utils.multiclass import type_of_target
from sklearn.utils.multiclass import class_distribution
from sklearn.utils.multiclass import check_non_regression_targets


class NotAnArray(object):
    """An object that is convertable to an array. This is useful to
    simulate a Pandas timeseries."""

    def __init__(self, data):
        self.data = data

    def __array__(self):
        return self.data


EXAMPLES = {
    'multilabel-indicator': [
        # valid when the data is formated as sparse or dense, identified
        # by CSR format when the testing takes place
        csr_matrix(np.random.RandomState(42).randint(2, size=(10, 10))),
        csr_matrix(np.array([[0, 1], [1, 0]])),
        csr_matrix(np.array([[0, 1], [1, 0]], dtype=np.bool)),
        csr_matrix(np.array([[0, 1], [1, 0]], dtype=np.int8)),
        csr_matrix(np.array([[0, 1], [1, 0]], dtype=np.uint8)),
        csr_matrix(np.array([[0, 1], [1, 0]], dtype=np.float)),
        csr_matrix(np.array([[0, 1], [1, 0]], dtype=np.float32)),
        csr_matrix(np.array([[0, 0], [0, 0]])),
        csr_matrix(np.array([[0, 1]])),
        # Only valid when data is dense
        np.array([[-1, 1], [1, -1]]),
        np.array([[-3, 3], [3, -3]]),
        NotAnArray(np.array([[-3, 3], [3, -3]])),
    ],
    'multiclass': [
        [1, 0, 2, 2, 1, 4, 2, 4, 4, 4],
        np.array([1, 0, 2]),
        np.array([1, 0, 2], dtype=np.int8),
        np.array([1, 0, 2], dtype=np.uint8),
        np.array([1, 0, 2], dtype=np.float),
        np.array([1, 0, 2], dtype=np.float32),
        np.array([[1], [0], [2]]),
        NotAnArray(np.array([1, 0, 2])),
        [0, 1, 2],
        ['a', 'b', 'c'],
        np.array([u'a', u'b', u'c']),
        np.array([u'a', u'b', u'c'], dtype=object),
        np.array(['a', 'b', 'c'], dtype=object),
    ],
    'multiclass-multioutput': [
        np.array([[1, 0, 2, 2], [1, 4, 2, 4]]),
        np.array([[1, 0, 2, 2], [1, 4, 2, 4]], dtype=np.int8),
        np.array([[1, 0, 2, 2], [1, 4, 2, 4]], dtype=np.uint8),
        np.array([[1, 0, 2, 2], [1, 4, 2, 4]], dtype=np.float),
        np.array([[1, 0, 2, 2], [1, 4, 2, 4]], dtype=np.float32),
        np.array([['a', 'b'], ['c', 'd']]),
        np.array([[u'a', u'b'], [u'c', u'd']]),
        np.array([[u'a', u'b'], [u'c', u'd']], dtype=object),
        np.array([[1, 0, 2]]),
        NotAnArray(np.array([[1, 0, 2]])),
    ],
    'binary': [
        [0, 1],
        [1, 1],
        [],
        [0],
        np.array([0, 1, 1, 1, 0, 0, 0, 1, 1, 1]),
        np.array([0, 1, 1, 1, 0, 0, 0, 1, 1, 1], dtype=np.bool),
        np.array([0, 1, 1, 1, 0, 0, 0, 1, 1, 1], dtype=np.int8),
        np.array([0, 1, 1, 1, 0, 0, 0, 1, 1, 1], dtype=np.uint8),
        np.array([0, 1, 1, 1, 0, 0, 0, 1, 1, 1], dtype=np.float),
        np.array([0, 1, 1, 1, 0, 0, 0, 1, 1, 1], dtype=np.float32),
        np.array([[0], [1]]),
        NotAnArray(np.array([[0], [1]])),
        [1, -1],
        [3, 5],
        ['a'],
        ['a', 'b'],
        ['abc', 'def'],
        np.array(['abc', 'def']),
        [u'a', u'b'],
        np.array(['abc', 'def'], dtype=object),
    ],
    'continuous': [
        [1e-5],
        [0, .5],
        np.array([[0], [.5]]),
        np.array([[0], [.5]], dtype=np.float32),
    ],
    'continuous-multioutput': [
        np.array([[0, .5], [.5, 0]]),
        np.array([[0, .5], [.5, 0]], dtype=np.float32),
        np.array([[0, .5]]),
    ],
    'unknown': [
        [[]],
        [()],
        # sequence of sequences that were'nt supported even before deprecation
        np.array([np.array([]), np.array([1, 2, 3])], dtype=object),
        [np.array([]), np.array([1, 2, 3])],
        [set([1, 2, 3]), set([1, 2])],
        [frozenset([1, 2, 3]), frozenset([1, 2])],

        # and also confusable as sequences of sequences
        [{0: 'a', 1: 'b'}, {0: 'a'}],

        # empty second dimension
        np.array([[], []]),

        # 3d
        np.array([[[0, 1], [2, 3]], [[4, 5], [6, 7]]]),
    ]
}

NON_ARRAY_LIKE_EXAMPLES = [
    set([1, 2, 3]),
    {0: 'a', 1: 'b'},
    {0: [5], 1: [5]},
    'abc',
    frozenset([1, 2, 3]),
    None,
]

MULTILABEL_SEQUENCES = [
    [[1], [2], [0, 1]],
    [(), (2), (0, 1)],
    np.array([[], [1, 2]], dtype='object'),
    NotAnArray(np.array([[], [1, 2]], dtype='object'))
]


def test_unique_labels():
    # Empty iterable
    assert_raises(ValueError, unique_labels)

    # Multiclass problem
    assert_array_equal(unique_labels(xrange(10)), np.arange(10))
    assert_array_equal(unique_labels(np.arange(10)), np.arange(10))
    assert_array_equal(unique_labels([4, 0, 2]), np.array([0, 2, 4]))

    # Multilabel indicator
    assert_array_equal(unique_labels(np.array([[0, 0, 1],
                                               [1, 0, 1],
                                               [0, 0, 0]])),
                       np.arange(3))

    assert_array_equal(unique_labels(np.array([[0, 0, 1],
                                               [0, 0, 0]])),
                       np.arange(3))

    # Several arrays passed
    assert_array_equal(unique_labels([4, 0, 2], xrange(5)),
                       np.arange(5))
    assert_array_equal(unique_labels((0, 1, 2), (0,), (2, 1)),
                       np.arange(3))

    # Border line case with binary indicator matrix
    assert_raises(ValueError, unique_labels, [4, 0, 2], np.ones((5, 5)))
    assert_raises(ValueError, unique_labels, np.ones((5, 4)), np.ones((5, 5)))
    assert_array_equal(unique_labels(np.ones((4, 5)), np.ones((5, 5))),
                       np.arange(5))


def test_unique_labels_non_specific():
    # Test unique_labels with a variety of collected examples

    # Smoke test for all supported format
    for format in ["binary", "multiclass", "multilabel-indicator"]:
        for y in EXAMPLES[format]:
            unique_labels(y)

    # We don't support those format at the moment
    for example in NON_ARRAY_LIKE_EXAMPLES:
        assert_raises(ValueError, unique_labels, example)

    for y_type in ["unknown", "continuous", 'continuous-multioutput',
                   'multiclass-multioutput']:
        for example in EXAMPLES[y_type]:
            assert_raises(ValueError, unique_labels, example)


def test_unique_labels_mixed_types():
    # Mix with binary or multiclass and multilabel
    mix_clf_format = product(EXAMPLES["multilabel-indicator"],
                             EXAMPLES["multiclass"] +
                             EXAMPLES["binary"])

    for y_multilabel, y_multiclass in mix_clf_format:
        assert_raises(ValueError, unique_labels, y_multiclass, y_multilabel)
        assert_raises(ValueError, unique_labels, y_multilabel, y_multiclass)

    assert_raises(ValueError, unique_labels, [[1, 2]], [["a", "d"]])
    assert_raises(ValueError, unique_labels, ["1", 2])
    assert_raises(ValueError, unique_labels, [["1", 2], [1, 3]])
    assert_raises(ValueError, unique_labels, [["1", "2"], [2, 3]])


def test_is_multilabel():
    for group, group_examples in iteritems(EXAMPLES):
        if group in ['multilabel-indicator']:
            dense_assert_, dense_exp = assert_true, 'True'
        else:
            dense_assert_, dense_exp = assert_false, 'False'

        for example in group_examples:
            # Only mark explicitly defined sparse examples as valid sparse
            # multilabel-indicators
            if group == 'multilabel-indicator' and issparse(example):
                sparse_assert_, sparse_exp = assert_true, 'True'
            else:
                sparse_assert_, sparse_exp = assert_false, 'False'

            if (issparse(example) or
                (hasattr(example, '__array__') and
                 np.asarray(example).ndim == 2 and
                 np.asarray(example).dtype.kind in 'biuf' and
                 np.asarray(example).shape[1] > 0)):
                examples_sparse = [sparse_matrix(example)
                                   for sparse_matrix in [coo_matrix,
                                                         csc_matrix,
                                                         csr_matrix,
                                                         dok_matrix,
                                                         lil_matrix]]
                for exmpl_sparse in examples_sparse:
                    sparse_assert_(is_multilabel(exmpl_sparse),
                                   msg=('is_multilabel(%r)'
                                   ' should be %s')
                                   % (exmpl_sparse, sparse_exp))

            # Densify sparse examples before testing
            if issparse(example):
                example = example.toarray()

            dense_assert_(is_multilabel(example),
                          msg='is_multilabel(%r) should be %s'
                          % (example, dense_exp))

def test_check_non_regression_targets():
    for y_type in EXAMPLES.keys():
        if y_type in ["unknown", "continuous", 'continuous-multioutput']:
            for example in EXAMPLES[y_type]:
                assert_raises(ValueError, check_non_regression_targets, example)
        else:
            for example in EXAMPLES[y_type]:
                check_non_regression_targets(example)

# @ignore_warnings
def test_type_of_target():
    for group, group_examples in iteritems(EXAMPLES):
        for example in group_examples:
            assert_equal(type_of_target(example), group,
                         msg=('type_of_target(%r) should be %r, got %r'
                              % (example, group, type_of_target(example))))

    for example in NON_ARRAY_LIKE_EXAMPLES:
        msg_regex = 'Expected array-like \(array or non-string sequence\).*'
        assert_raises_regex(ValueError, msg_regex, type_of_target, example)

    for example in MULTILABEL_SEQUENCES:
        msg = ('You appear to be using a legacy multi-label data '
               'representation. Sequence of sequences are no longer supported;'
               ' use a binary array or sparse matrix instead.')
        assert_raises_regex(ValueError, msg, type_of_target, example)


def test_class_distribution():
    y = np.array([[1, 0, 0, 1],
                  [2, 2, 0, 1],
                  [1, 3, 0, 1],
                  [4, 2, 0, 1],
                  [2, 0, 0, 1],
                  [1, 3, 0, 1]])
    # Define the sparse matrix with a mix of implicit and explicit zeros
    data = np.array([1, 2, 1, 4, 2, 1, 0, 2, 3, 2, 3, 1, 1, 1, 1, 1, 1])
    indices = np.array([0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 5, 0, 1, 2, 3, 4, 5])
    indptr = np.array([0, 6, 11, 11, 17])
    y_sp = sp.csc_matrix((data, indices, indptr), shape=(6, 4))

    classes, n_classes, class_prior = class_distribution(y)
    classes_sp, n_classes_sp, class_prior_sp = class_distribution(y_sp)
    classes_expected = [[1, 2, 4],
                        [0, 2, 3],
                        [0],
                        [1]]
    n_classes_expected = [3, 3, 1, 1]
    class_prior_expected = [[3/6, 2/6, 1/6],
                            [1/3, 1/3, 1/3],
                            [1.0],
                            [1.0]]

    for k in range(y.shape[1]):
        assert_array_almost_equal(classes[k], classes_expected[k])
        assert_array_almost_equal(n_classes[k], n_classes_expected[k])
        assert_array_almost_equal(class_prior[k], class_prior_expected[k])

        assert_array_almost_equal(classes_sp[k], classes_expected[k])
        assert_array_almost_equal(n_classes_sp[k], n_classes_expected[k])
        assert_array_almost_equal(class_prior_sp[k], class_prior_expected[k])

    # Test again with explicit sample weights
    (classes,
     n_classes,
     class_prior) = class_distribution(y, [1.0, 2.0, 1.0, 2.0, 1.0, 2.0])
    (classes_sp,
     n_classes_sp,
     class_prior_sp) = class_distribution(y, [1.0, 2.0, 1.0, 2.0, 1.0, 2.0])
    class_prior_expected = [[4/9, 3/9, 2/9],
                            [2/9, 4/9, 3/9],
                            [1.0],
                            [1.0]]

    for k in range(y.shape[1]):
        assert_array_almost_equal(classes[k], classes_expected[k])
        assert_array_almost_equal(n_classes[k], n_classes_expected[k])
        assert_array_almost_equal(class_prior[k], class_prior_expected[k])

        assert_array_almost_equal(classes_sp[k], classes_expected[k])
        assert_array_almost_equal(n_classes_sp[k], n_classes_expected[k])
        assert_array_almost_equal(class_prior_sp[k], class_prior_expected[k])
