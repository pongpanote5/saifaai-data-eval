from evaluation.metrics import compute_cleanliness, compute_completeness


def test_cleanliness_bounds():
    assert 0.0 <= compute_cleanliness("") <= 1.0
    assert 0.0 <= compute_cleanliness("cookie privacy terms accept") <= 1.0
    assert 0.0 <= compute_cleanliness("line\nline\nline") <= 1.0


def test_completeness_bounds():
    baseline = "This is a baseline text with some content and words."
    candidate = "This baseline text has some words."
    assert 0.0 <= compute_completeness(baseline, candidate) <= 1.0
    assert 0.0 <= compute_completeness("", "") <= 1.0
    assert 0.0 <= compute_completeness(baseline, "") <= 1.0
