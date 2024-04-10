from src.cv import CVGenerator, CVSpec

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import KFold, RepeatedStratifiedKFold

N_SPLITS = 5
N_REPEATS = 1
RANDOM_STATE = 42
SHUFFLE = True

def test_cv_spec():
    cv_spec = CVSpec(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE, shuffle=SHUFFLE)
    assert cv_spec.n_splits == N_SPLITS
    assert cv_spec.n_repeats == N_REPEATS
    assert cv_spec.random_state == RANDOM_STATE
    assert cv_spec.shuffle == SHUFFLE

def test_cv_spec_repr():
    cv_spec = CVSpec(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE, shuffle=SHUFFLE)
    assert str(cv_spec) == f"\n\tNumber of splits: {N_SPLITS}\n\tNumber of repeats: {N_REPEATS}\n\tRandom state: {RANDOM_STATE}\n\tShuffle: {SHUFFLE}\n"

def test_cv_generator_attributes():
    cv_spec = CVSpec(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE, shuffle=SHUFFLE)
    cv = CVGenerator(cv_spec)
    assert cv.n_splits == N_SPLITS
    assert cv.n_repeats == N_REPEATS
    assert cv.random_state == RANDOM_STATE
    assert cv.shuffle == SHUFFLE

def test_generate_inner():
    cv_spec = CVSpec(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE, shuffle=SHUFFLE)
    cv = CVGenerator(cv_spec)
    cv_actual = cv.generate_inner()
    cv_expected = KFold(n_splits=N_SPLITS, shuffle=SHUFFLE, random_state=RANDOM_STATE)

    # assert objects are of the same 
    assert isinstance(cv_actual, KFold)
    assert cv_actual.n_splits == cv_expected.n_splits
    assert cv_actual.shuffle == cv_expected.shuffle
    assert cv_actual.random_state == cv_expected.random_state
    
def test_generate_outer():
    cv_spec = CVSpec(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE, shuffle=SHUFFLE)
    cv = CVGenerator(cv_spec)
    cv_actual = cv.generate_outer()
    cv_expected = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE)

    # assert objects are of the same
    assert isinstance(cv_actual, RepeatedStratifiedKFold)  
    assert cv_actual.n_repeats == cv_expected.n_repeats
    assert cv_actual.random_state == cv_expected.random_state
    
def test_generate_grid_search():
    cv_spec = CVSpec(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=RANDOM_STATE, shuffle=SHUFFLE)
    cv = CVGenerator(cv_spec)
    grid_search = cv.generate_grid_search(pipeline=None, param_grid={})
    assert isinstance(grid_search, GridSearchCV)


