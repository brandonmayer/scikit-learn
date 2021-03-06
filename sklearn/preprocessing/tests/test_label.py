import numpy as np

from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_true
from sklearn.utils.testing import assert_false
from sklearn.utils.testing import assert_warns
from sklearn.utils.testing import ignore_warnings

from sklearn.preprocessing.label import LabelBinarizer
from sklearn.preprocessing.label import MultiLabelBinarizer
from sklearn.preprocessing.label import LabelEncoder
from sklearn.preprocessing.label import label_binarize


from sklearn import datasets
from sklearn.linear_model.stochastic_gradient import SGDClassifier

iris = datasets.load_iris()


def toarray(a):
    if hasattr(a, "toarray"):
        a = a.toarray()
    return a


def test_label_binarizer():
    lb = LabelBinarizer()

    # two-class case
    inp = ["neg", "pos", "pos", "neg"]
    expected = np.array([[0, 1, 1, 0]]).T
    got = lb.fit_transform(inp)
    assert_false(lb.multilabel_)
    assert_array_equal(lb.classes_, ["neg", "pos"])
    assert_array_equal(expected, got)
    assert_array_equal(lb.inverse_transform(got), inp)

    # multi-class case
    inp = ["spam", "ham", "eggs", "ham", "0"]
    expected = np.array([[0, 0, 0, 1],
                         [0, 0, 1, 0],
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [1, 0, 0, 0]])
    got = lb.fit_transform(inp)
    assert_array_equal(lb.classes_, ['0', 'eggs', 'ham', 'spam'])
    assert_false(lb.multilabel_)
    assert_array_equal(expected, got)
    assert_array_equal(lb.inverse_transform(got), inp)


@ignore_warnings
def test_label_binarizer_column_y():
    # first for binary classification vs multi-label with 1 possible class
    # lists are multi-label, array is multi-class :-/
    inp_list = [[1], [2], [1]]
    inp_array = np.array(inp_list)

    multilabel_indicator = np.array([[1, 0], [0, 1], [1, 0]])
    binaryclass_array = np.array([[0], [1], [0]])

    lb_1 = LabelBinarizer()
    out_1 = lb_1.fit_transform(inp_list)

    lb_2 = LabelBinarizer()
    out_2 = lb_2.fit_transform(inp_array)

    assert_array_equal(out_1, multilabel_indicator)
    assert_true(lb_1.multilabel_)

    assert_array_equal(out_2, binaryclass_array)
    assert_false(lb_2.multilabel_)

    # second for multiclass classification vs multi-label with multiple
    # classes
    inp_list = [[1], [2], [1], [3]]
    inp_array = np.array(inp_list)

    # the indicator matrix output is the same in this case
    indicator = np.array([[1, 0, 0], [0, 1, 0], [1, 0, 0], [0, 0, 1]])

    lb_1 = LabelBinarizer()
    out_1 = lb_1.fit_transform(inp_list)

    lb_2 = LabelBinarizer()
    out_2 = lb_2.fit_transform(inp_array)

    assert_array_equal(out_1, out_2)
    assert_true(lb_1.multilabel_)

    assert_array_equal(out_2, indicator)
    assert_false(lb_2.multilabel_)


def test_label_binarizer_set_label_encoding():
    lb = LabelBinarizer(neg_label=-2, pos_label=2)

    # two-class case
    inp = np.array([0, 1, 1, 0])
    expected = np.array([[-2, 2, 2, -2]]).T
    got = lb.fit_transform(inp)
    assert_false(lb.multilabel_)
    assert_array_equal(expected, got)
    assert_array_equal(lb.inverse_transform(got), inp)

    # multi-class case
    inp = np.array([3, 2, 1, 2, 0])
    expected = np.array([[-2, -2, -2, +2],
                         [-2, -2, +2, -2],
                         [-2, +2, -2, -2],
                         [-2, -2, +2, -2],
                         [+2, -2, -2, -2]])
    got = lb.fit_transform(inp)
    assert_false(lb.multilabel_)
    assert_array_equal(expected, got)
    assert_array_equal(lb.inverse_transform(got), inp)


def test_label_binarizer_multilabel():
    lb = LabelBinarizer()

    # test input as lists of tuples
    inp = [(2, 3), (1,), (1, 2)]
    indicator_mat = np.array([[0, 1, 1],
                              [1, 0, 0],
                              [1, 1, 0]])
    got = assert_warns(DeprecationWarning, lb.fit_transform, inp)
    assert_true(lb.multilabel_)
    assert_array_equal(indicator_mat, got)
    assert_equal(lb.inverse_transform(got), inp)

    # test input as label indicator matrix
    lb.fit(indicator_mat)
    assert_array_equal(indicator_mat,
                       lb.inverse_transform(indicator_mat))

    # regression test for the two-class multilabel case
    lb = LabelBinarizer()
    inp = [[1, 0], [0], [1], [0, 1]]
    expected = np.array([[1, 1],
                         [1, 0],
                         [0, 1],
                         [1, 1]])
    got = assert_warns(DeprecationWarning, lb.fit_transform, inp)
    assert_true(lb.multilabel_)
    assert_array_equal(expected, got)
    assert_equal([set(x) for x in lb.inverse_transform(got)],
                 [set(x) for x in inp])


def test_label_binarizer_errors():
    """Check that invalid arguments yield ValueError"""
    one_class = np.array([0, 0, 0, 0])
    lb = LabelBinarizer().fit(one_class)
    assert_false(lb.multilabel_)

    multi_label = np.array([[0, 0, 1, 0], [1, 0, 1, 0]])
    assert_raises(ValueError, lb.transform, multi_label)

    lb = LabelBinarizer()
    assert_raises(ValueError, lb.transform, [])
    assert_raises(ValueError, lb.inverse_transform, [])

    assert_raises(ValueError, LabelBinarizer, neg_label=2, pos_label=1)
    assert_raises(ValueError, LabelBinarizer, neg_label=2, pos_label=2)


def test_label_encoder():
    """Test LabelEncoder's transform and inverse_transform methods"""
    le = LabelEncoder()
    le.fit([1, 1, 4, 5, -1, 0])
    assert_array_equal(le.classes_, [-1, 0, 1, 4, 5])
    assert_array_equal(le.transform([0, 1, 4, 4, 5, -1, -1]),
                       [1, 2, 3, 3, 4, 0, 0])
    assert_array_equal(le.inverse_transform([1, 2, 3, 3, 4, 0, 0]),
                       [0, 1, 4, 4, 5, -1, -1])
    assert_raises(ValueError, le.transform, [0, 6])


def test_label_encoder_fit_transform():
    """Test fit_transform"""
    le = LabelEncoder()
    ret = le.fit_transform([1, 1, 4, 5, -1, 0])
    assert_array_equal(ret, [2, 2, 3, 4, 0, 1])

    le = LabelEncoder()
    ret = le.fit_transform(["paris", "paris", "tokyo", "amsterdam"])
    assert_array_equal(ret, [1, 1, 2, 0])


def test_label_encoder_string_labels():
    """Test LabelEncoder's transform and inverse_transform methods with
    non-numeric labels"""
    le = LabelEncoder()
    le.fit(["paris", "paris", "tokyo", "amsterdam"])
    assert_array_equal(le.classes_, ["amsterdam", "paris", "tokyo"])
    assert_array_equal(le.transform(["tokyo", "tokyo", "paris"]),
                       [2, 2, 1])
    assert_array_equal(le.inverse_transform([2, 2, 1]),
                       ["tokyo", "tokyo", "paris"])
    assert_raises(ValueError, le.transform, ["london"])


def test_label_encoder_errors():
    """Check that invalid arguments yield ValueError"""
    le = LabelEncoder()
    assert_raises(ValueError, le.transform, [])
    assert_raises(ValueError, le.inverse_transform, [])


def test_label_binarizer_iris():
    lb = LabelBinarizer()
    Y = lb.fit_transform(iris.target)
    clfs = [SGDClassifier().fit(iris.data, Y[:, k])
            for k in range(len(lb.classes_))]
    Y_pred = np.array([clf.decision_function(iris.data) for clf in clfs]).T
    y_pred = lb.inverse_transform(Y_pred)
    accuracy = np.mean(iris.target == y_pred)
    y_pred2 = SGDClassifier().fit(iris.data, iris.target).predict(iris.data)
    accuracy2 = np.mean(iris.target == y_pred2)
    assert_almost_equal(accuracy, accuracy2)


def test_label_binarizer_multilabel_unlabeled():
    """Check that LabelBinarizer can handle an unlabeled sample"""
    lb = LabelBinarizer()
    y = [[1, 2], [1], []]
    Y = np.array([[1, 1],
                  [1, 0],
                  [0, 0]])
    assert_array_equal(assert_warns(DeprecationWarning,
                                    lb.fit_transform, y), Y)


def test_label_binarize_with_multilabel_indicator():
    """Check that passing a binary indicator matrix is not noop"""

    classes = np.arange(3)
    neg_label = -1
    pos_label = 2

    y = np.array([[0, 1, 0], [1, 1, 1]])
    expected = np.array([[-1, 2, -1], [2, 2, 2]])

    # With label binarize
    output = label_binarize(y, classes, multilabel=True, neg_label=neg_label,
                            pos_label=pos_label)
    assert_array_equal(output, expected)

    # With the transformer
    lb = LabelBinarizer(pos_label=pos_label, neg_label=neg_label)
    output = lb.fit_transform(y)
    assert_array_equal(output, expected)

    output = lb.fit(y).transform(y)
    assert_array_equal(output, expected)


def test_mutlilabel_binarizer():
    # test input as iterable of iterables
    inputs = [
        lambda: [(2, 3), (1,), (1, 2)],
        lambda: (set([2, 3]), set([1]), set([1, 2])),
        lambda: iter([iter((2, 3)), iter((1,)), set([1, 2])]),
    ]
    indicator_mat = np.array([[0, 1, 1],
                              [1, 0, 0],
                              [1, 1, 0]])
    inverse = inputs[0]()
    for inp in inputs:
        # With fit_tranform
        mlb = MultiLabelBinarizer()
        got = mlb.fit_transform(inp())
        assert_array_equal(indicator_mat, got)
        assert_array_equal([1, 2, 3], mlb.classes_)
        assert_equal(mlb.inverse_transform(got), inverse)

        # With fit
        mlb = MultiLabelBinarizer()
        got = mlb.fit(inp()).transform(inp())
        assert_array_equal(indicator_mat, got)
        assert_array_equal([1, 2, 3], mlb.classes_)
        assert_equal(mlb.inverse_transform(got), inverse)


def test_mutlilabel_binarizer_empty_sample():
    mlb = MultiLabelBinarizer()
    y = [[1, 2], [1], []]
    Y = np.array([[1, 1],
                  [1, 0],
                  [0, 0]])
    assert_array_equal(mlb.fit_transform(y), Y)


def test_mutlilabel_binarizer_unknown_class():
    mlb = MultiLabelBinarizer()
    y = [[1, 2]]
    assert_raises(KeyError, mlb.fit(y).transform, [[0]])

    mlb = MultiLabelBinarizer(classes=[1, 2])
    assert_raises(KeyError, mlb.fit_transform, [[0]])


def test_mutlilabel_binarizer_given_classes():
    inp = [(2, 3), (1,), (1, 2)]
    indicator_mat = np.array([[0, 1, 1],
                              [1, 0, 0],
                              [1, 0, 1]])
    # fit_transform()
    mlb = MultiLabelBinarizer(classes=[1, 3, 2])
    assert_array_equal(mlb.fit_transform(inp), indicator_mat)
    assert_array_equal(mlb.classes_, [1, 3, 2])

    # fit().transform()
    mlb = MultiLabelBinarizer(classes=[1, 3, 2])
    assert_array_equal(mlb.fit(inp).transform(inp), indicator_mat)
    assert_array_equal(mlb.classes_, [1, 3, 2])

    # ensure works with extra class
    mlb = MultiLabelBinarizer(classes=[4, 1, 3, 2])
    assert_array_equal(mlb.fit_transform(inp),
                       np.hstack(([[0], [0], [0]], indicator_mat)))
    assert_array_equal(mlb.classes_, [4, 1, 3, 2])

    # ensure fit is no-op as iterable is not consumed
    inp = iter(inp)
    mlb = MultiLabelBinarizer(classes=[1, 3, 2])
    assert_array_equal(mlb.fit(inp).transform(inp), indicator_mat)


def test_mutlilabel_binarizer_same_length_sequence():
    """Ensure sequences of the same length are not interpreted as a 2-d array
    """
    inp = [[1], [0], [2]]
    indicator_mat = np.array([[0, 1, 0],
                              [1, 0, 0],
                              [0, 0, 1]])
    # fit_transform()
    mlb = MultiLabelBinarizer()
    assert_array_equal(mlb.fit_transform(inp), indicator_mat)
    assert_array_equal(mlb.inverse_transform(indicator_mat), inp)

    # fit().transform()
    mlb = MultiLabelBinarizer()
    assert_array_equal(mlb.fit(inp).transform(inp), indicator_mat)
    assert_array_equal(mlb.inverse_transform(indicator_mat), inp)


def test_mutlilabel_binarizer_non_integer_labels():
    tuple_classes = np.empty(3, dtype=object)
    tuple_classes[:] = [(1,), (2,), (3,)]
    inputs = [
        ([('2', '3'), ('1',), ('1', '2')], ['1', '2', '3']),
        ([('b', 'c'), ('a',), ('a', 'b')], ['a', 'b', 'c']),
        ([((2,), (3,)), ((1,),), ((1,), (2,))], tuple_classes),
    ]
    indicator_mat = np.array([[0, 1, 1],
                              [1, 0, 0],
                              [1, 1, 0]])
    for inp, classes in inputs:
        # fit_transform()
        mlb = MultiLabelBinarizer()
        assert_array_equal(mlb.fit_transform(inp), indicator_mat)
        assert_array_equal(mlb.classes_, classes)
        assert_array_equal(mlb.inverse_transform(indicator_mat), inp)

        # fit().transform()
        mlb = MultiLabelBinarizer()
        assert_array_equal(mlb.fit(inp).transform(inp), indicator_mat)
        assert_array_equal(mlb.classes_, classes)
        assert_array_equal(mlb.inverse_transform(indicator_mat), inp)

    mlb = MultiLabelBinarizer()
    assert_raises(TypeError, mlb.fit_transform, [({}), ({}, {'a': 'b'})])


def test_mutlilabel_binarizer_non_unique():
    inp = [(1, 1, 1, 0)]
    indicator_mat = np.array([[1, 1]])
    mlb = MultiLabelBinarizer()
    assert_array_equal(mlb.fit_transform(inp), indicator_mat)


def test_multilabel_binarizer_inverse_validation():
    inp = [(1, 1, 1, 0)]
    mlb = MultiLabelBinarizer()
    mlb.fit_transform(inp)
    # Not binary
    assert_raises(ValueError, mlb.inverse_transform, np.array([[1, 3]]))
    # The following binary cases are fine, however
    mlb.inverse_transform(np.array([[0, 0]]))
    mlb.inverse_transform(np.array([[1, 1]]))
    mlb.inverse_transform(np.array([[1, 0]]))

    # Wrong shape
    assert_raises(ValueError, mlb.inverse_transform, np.array([[1]]))
    assert_raises(ValueError, mlb.inverse_transform, np.array([[1, 1, 1]]))
