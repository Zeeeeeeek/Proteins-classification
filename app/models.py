import sys

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.cluster import AgglomerativeClustering, AffinityPropagation, MeanShift
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, Normalizer
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

"""
Usage: python models.py <path_to_csv> <level> <method> <max_sample_size_per_level> <k> [random_state]
"""


def get_y_and_X(df, level: str):
    X = df.copy()

    match level:
        case "class":
            X['label'] = df.apply(lambda row: row["class_topology_fold_clan"].split(".")[0] if len(
                row["class_topology_fold_clan"].split(".")) > 0 else np.nan, axis=1)
        case "topology":
            X['label'] = df.apply(lambda row: row["class_topology_fold_clan"].split(".")[1] if len(
                row["class_topology_fold_clan"].split(".")) > 1 else np.nan, axis=1)
        case "fold":
            X['label'] = df.apply(lambda row: row["class_topology_fold_clan"].split(".")[2] if len(
                row["class_topology_fold_clan"].split(".")) > 2 else np.nan, axis=1)
        case "clan":
            X['label'] = df.apply(lambda row: row["class_topology_fold_clan"].split(".")[3] if len(
                row["class_topology_fold_clan"].split(".")) > 3 else np.nan, axis=1)
        case _:
            raise ValueError(f"Error: {level} is not a valid level. Please use one of the following: "
                             f"class, topology, fold, clan, class_topology, class_topology_fold, "
                             f"class_topology_fold_clan.")
    X.dropna(subset=["label"], inplace=True)
    return X['label'].astype(str), X.drop(columns=["class_topology_fold_clan",
                                                   "region_id", "label"])


def get_classifiers(random_state):
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
        SVC(random_state=random_state),
        DecisionTreeClassifier(random_state=random_state),
        RandomForestClassifier(random_state=random_state),
        RandomForestClassifier(random_state=random_state, criterion='log_loss'),
        MLPClassifier(random_state=random_state),
        GaussianNB()
    ]
    return names, classifiers


def get_classifiers_results(X, y, random_state):
    names, classifiers = get_classifiers(random_state)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=random_state)
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
    return results


def get_classifiers_results_with_k_fold(X, y, random_state):
    names, models = get_classifiers(random_state)
    scores = {}

    for name, model in zip(names, models):
        scoring = {
            "Accuracy": make_scorer(metrics.accuracy_score),
            "Precision": make_scorer(metrics.precision_score, average='weighted', zero_division=1),
            "Recall": make_scorer(metrics.recall_score, average='weighted', zero_division=1),
            "F1 score": make_scorer(metrics.f1_score, average='weighted')
        }
        cv_results = cross_validate(model, X, y, cv=5, scoring=scoring)

        scores[name] = {
            "Accuracy": cv_results['test_Accuracy'].mean(),
            "Precision": cv_results['test_Precision'].mean(),
            "Recall": cv_results['test_Recall'].mean(),
            "F1 Score": cv_results['test_F1 score'].mean()
        }

    return scores


def print_results(results):
    for classifier, met in results.items():
        print("=" * 30 + "\n")
        print(classifier)
        print("\nMetrics:")
        for metric, value in met.items():
            if value is not None:
                print(f"\t{metric}: {value:.4f}")
            else:
                print(f"\t{metric}: N/A")
        print()


def print_cluster_metrics(labels_true, labels_pred, method: str, data, random_state):
    print("=" * 30)
    print(f"{method}")
    print("\tSilhouette_score", metrics.silhouette_score(data, labels_pred, random_state=random_state))
    print("\tRand_score", metrics.rand_score(labels_true, labels_pred))
    print("\tHomogeneity_score", metrics.homogeneity_score(labels_true, labels_pred))
    print("\tCompleteness_score", metrics.completeness_score(labels_true, labels_pred))


def clustering(X, labels, random_state):
    clusters = [
        AgglomerativeClustering(n_clusters=len(set(labels))),
        # DBSCAN(),
        AffinityPropagation(random_state=random_state),
        MeanShift()
    ]

    names = [
        "Agglomerative Clustering",
        # "DBSCAN",
        "Affinity Propagation",
        "Mean Shift"
    ]

    for index, model in enumerate(clusters):
        model.fit(X)
        print_cluster_metrics(labels, model.labels_, names[index], X, random_state)


def get_sampled_regions(df_path, level: str, sample_size: int, random_state):
    df = pd.read_csv(df_path, usecols=["region_id", "class_topology_fold_clan"],
                     dtype={"region_id": str, "class_topology_fold_clan": str})
    df['label'], _ = get_y_and_X(df, level)
    counter = df['label'].value_counts().to_dict()
    for key, count in counter.items():
        if count > sample_size:
            counter[key] = sample_size
    return \
        df.groupby('label').apply(lambda x: x.sample(n=counter[x.name], random_state=random_state),
                                  include_groups=False)[
            'region_id'].tolist()


def read_csv_of_regions(df_path, regions, k):
    index = 0
    rows = []
    reg_copy = regions.copy()
    with open(df_path, "r") as file:
        for line in file:
            if index == 0:
                columns = line.strip().split(",")
                # Filter all kmer columns that are not in the range [1, k], excluding the first 3 columns
                columns_indexes = [0, 1, 2] + [i + 3 for i, c in enumerate(columns[3:]) if len(c) <= k]
                columns = [columns[i] for i in columns_indexes]
                index += 1
                if len(columns) == 3:
                    raise ValueError("Error: no kmer columns found.")
                continue
            split = line.strip().split(",")
            if split[0] in reg_copy:
                row = []
                for i in columns_indexes:
                    if i > 2:
                        row.append(int(split[i]) if split[i] != '' else 0)
                    else:
                        row.append(split[i])
                rows.append(row)
                reg_copy.remove(split[0])
            if len(reg_copy) == 0:
                break
    print("\tCreating DataFrame...")
    df = pd.DataFrame(rows, columns=columns)
    # print(df.shape)
    # to_drop = []
    # for col in df.columns[3:]:
    #    if df[col].sum() == 0:
    #        to_drop.append(col)
    # df.drop(columns=to_drop, inplace=True)
    # print(df.shape)
    # df.to_csv("test.csv", index=False)
    # Standardize data
    # print("\tStandardizing data...")
    # scaler = StandardScaler()
    # df[df.columns[3:]] = scaler.fit_transform(df[df.columns[3:]])
    # print("\tNormalizing data...")
    # normalizer = Normalizer()
    # df[df.columns[3:]] = normalizer.fit_transform(df[df.columns[3:]])

    return df


def get_best_classifier(results):
    max_dict = {
        "Accuracy": 0,
        "Precision": 0,
        "Recall": 0,
        "F1 Score": 0
    }
    for classifier, met in results.items():
        for metric, value in met.items():
            if value > max_dict[metric]:
                max_dict[metric] = value
    scores = {}  # Each classifier with the best metric gains a point
    for classifier, met in results.items():
        for metric, value in met.items():
            if value == max_dict[metric]:
                if classifier in scores:
                    scores[classifier] += 1
                else:
                    scores[classifier] = 1
    # Sort by points
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    result = []
    best_found = False
    for classifier, points in sorted_scores.items():
        if not best_found:
            result.append(classifier)
            best_found = True
        else:
            if points == list(sorted_scores.values())[0]:
                result.append(classifier)
            else:
                break
    return result


def run_models(df_path, level, method, max_sample_size_per_level, k, random_state=42):
    if method not in ['clustering', 'classifiers']:
        raise ValueError("Error: method must be either 'cluster' or 'classifiers'.")
    if max_sample_size_per_level < 1 or not isinstance(max_sample_size_per_level, int):
        raise ValueError("Error: max_sample_size_per_level must be an integer greater than 0.")
    print("Reading CSV...")
    print("\tSampling regions...")
    sampled_regions = get_sampled_regions(df_path, level, max_sample_size_per_level, random_state)
    print("\tReading data...")
    df = read_csv_of_regions(df_path, sampled_regions, k)
    y, X = get_y_and_X(df, level)
    print(len(y))
    if 'sequence' in X.columns:
        X.drop(columns=['sequence'], inplace=True)
    if method == 'clustering':
        print("Clustering...")
        clustering(X, y, random_state)
    else:
        print("Running classifiers...")
        print_results(get_classifiers_results_with_k_fold(X, y, random_state))
        print("Best classifier(s):", get_best_classifier(get_classifiers_results_with_k_fold(X, y, random_state)))
    print("Done.")


def main():
    run_models(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))


if __name__ == "__main__":
    main()
