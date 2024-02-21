import sys

import pandas as pd
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelBinarizer
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

"""
Usage: python models.py <path_to_csv> <level>
"""
RANDOM_STATE = 42


def get_y_from_df_and_level(df, level: str):
    match level:
        case "class":
            return df.apply(lambda row: row["class_topology_fold_clan"].split(".")[0], axis=1)
        case "topology":
            return df.apply(lambda row: row["class_topology_fold_clan"].split(".")[1], axis=1)
        case "fold":
            return df.apply(lambda row: row["class_topology_fold_clan"].split(".")[2], axis=1)
        case "clan":
            return df.apply(lambda row: row["class_topology_fold_clan"].split(".")[3], axis=1)
        case "class_topology":
            return df.apply(lambda row: ".".join(row["class_topology_fold_clan"].split(".")[0:2]), axis=1)
        case "class_topology_fold":
            return df.apply(lambda row: ".".join(row["class_topology_fold_clan"].split(".")[0:3]), axis=1)
        case "class_topology_fold_clan":
            return df["class_topology_fold_clan"]
        case _:
            raise ValueError(f"Error: {level} is not a valid level. Please use one of the following: "
                             f"class, topology, fold, clan, class_topology, class_topology_fold, "
                             f"class_topology_fold_clan.")


def get_classifiers_results(X, y):
    names = [
        "K Nearest Neighbors",
        "SVM",
        "Decision Tree",
        "Random Forest",
        "Random Forest Log Loss",
        "Neural Net",
        "Naive Bayes"
    ]
    classifiers = [
        KNeighborsClassifier(),
        SVC(random_state=RANDOM_STATE),
        DecisionTreeClassifier(random_state=RANDOM_STATE),
        RandomForestClassifier(random_state=RANDOM_STATE),
        RandomForestClassifier(random_state=RANDOM_STATE, criterion='log_loss'),
        MLPClassifier(random_state=RANDOM_STATE, max_iter=1000),
        GaussianNB()
    ]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=RANDOM_STATE)
    results = {}
    for index, classifier in enumerate(classifiers):
        classifier_name = names[index]
        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)
        results[classifier_name] = {}
        results[classifier_name]["Accuracy"] = metrics.accuracy_score(y_test, y_pred)
        results[classifier_name]["Precision"] = metrics.precision_score(y_test, y_pred, average='weighted',
                                                                        zero_division=1)
        results[classifier_name]["Recall"] = metrics.recall_score(y_test, y_pred, average='weighted',
                                                                  zero_division=1)
        results[classifier_name]["F1 Score"] = metrics.f1_score(y_test, y_pred, average='weighted')
        lb = LabelBinarizer()
        lb.fit(y_test)
        y_test_lb = lb.transform(y_test)
        y_pred_lb = lb.transform(y_pred)
        results[classifier_name]["AUC-ROC"] = metrics.roc_auc_score(y_test_lb, y_pred_lb, average='weighted',
                                                                    multi_class='ovr')
    return results


def print_results(results):
    for classifier, met in results.items():
        print("=" * 30)
        print(classifier)
        print("\nMetrics:")
        for metric, value in met.items():
            print(f"\t{metric}: {value:.4f}")
        print()


def main():
    if len(sys.argv) != 3:
        raise ValueError("Usage: python models.py <path_to_csv> <level>")
    df = pd.read_csv(sys.argv[1])
    y = get_y_from_df_and_level(df, sys.argv[2])
    X = df.drop(columns=["class_topology_fold_clan", "sequence", "region_id"]).fillna(0)
    results = get_classifiers_results(X, y)
    print_results(results)


if __name__ == "__main__":
    main()
