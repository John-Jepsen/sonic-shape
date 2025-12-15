import pandas as pd

from classically_punk.models.baseline import evaluate_classifier, train_baseline_classifier


def test_train_and_evaluate_baseline_classifier():
    # Construct a simple separable dataset.
    data = []
    for i in range(30):
        data.append({"label": "rock", "feat_a": 2.0 + 0.1 * i, "feat_b": 0.1})
    for i in range(30):
        data.append({"label": "jazz", "feat_a": 0.1, "feat_b": 2.0 + 0.1 * i})

    df = pd.DataFrame(data)

    clf, X_test, y_test = train_baseline_classifier(df, target_col="label", test_size=0.25, random_state=0)
    metrics = evaluate_classifier(clf, X_test, y_test)

    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1_macro"] <= 1.0
    assert "rock" in metrics["report"]
