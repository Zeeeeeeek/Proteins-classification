import sys
from typing import Callable, List, Tuple, Any, Set

import pandas as pd
from sklearn import metrics
from sklearn.cluster import AgglomerativeClustering, AffinityPropagation
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_validate
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import Normalizer, StandardScaler
from sklearn.svm import SVC

"""
Usage: python models.py <path_to_csv> <level> <method> <max_sample_size_per_level> <k> [random_state]
"""


def get_y_and_X(df, level: str):
    X = df.copy()

    match level:
        case "class":
            X['label'] = df.apply(lambda row: row["class_topology_fold_clan"].split(".")[0] if len(
                row["class_topology_fold_clan"].split(".")) > 0 else "N/A", axis=1)
        case "topology":
            X['label'] = df.apply(lambda row: row["class_topology_fold_clan"].split(".")[1] if len(
                row["class_topology_fold_clan"].split(".")) > 1 else "N/A", axis=1)
        case "fold":
            X['label'] = df.apply(lambda row: row["class_topology_fold_clan"].split(".")[2] if len(
                row["class_topology_fold_clan"].split(".")) > 2 else "N/A", axis=1)
        case "clan":
            X['label'] = df.apply(lambda row: row["class_topology_fold_clan"].split(".")[3] if len(
                row["class_topology_fold_clan"].split(".")) > 3 else "N/A", axis=1)
        case _:
            raise ValueError(f"Error: {level} is not a valid level. Please use one of the following: "
                             f"class, topology, fold, clan")

    return X['label'].astype(str), X.drop(columns=["class_topology_fold_clan",
                                                   "region_id", "label"])


def get_classifiers(random_state):
    names = [
        "SVM",
        "Random Forest",
        "MLPClassifier",
        "GaussianNB"
    ]
    classifiers = [
        SVC(random_state=random_state),
        RandomForestClassifier(random_state=random_state),
        MLPClassifier(random_state=random_state, max_iter=500),
        GaussianNB()
    ]
    return names, classifiers


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


def get_clustering_models(random_state, labels: Set[str]):
    clusters = [
        AgglomerativeClustering(n_clusters=len(labels)),
        AgglomerativeClustering(n_clusters=len(labels), linkage='complete'),
        AgglomerativeClustering(n_clusters=len(labels), linkage='average'),
        AffinityPropagation(random_state=random_state, damping=0.9, max_iter=1000),
        AffinityPropagation(random_state=random_state, damping=0.9, max_iter=1500),
    ]

    names = [
        "Agglomerative Clustering (Ward)",
        "Agglomerative Clustering Complete Linkage",
        "Agglomerative Clustering Average Linkage",
        "Affinity Propagation",
        "Affinity Propagation (1500 iterations)"
    ]
    return zip(names, clusters)


def clustering(X, labels, random_state,
               models_provider: Callable[[int, Set[str]], List[Tuple[str, Any]]] = get_clustering_models):
    scores = {}
    for name, model in models_provider(random_state, set(labels)):
        model.fit(X)
        scores[name] = {
            "Silhouette Score": metrics.silhouette_score(X, model.labels_, random_state=random_state),
            "Rand Score": metrics.rand_score(labels, model.labels_),
            "Homogeneity Score": metrics.homogeneity_score(labels, model.labels_),
            "Completeness Score": metrics.completeness_score(labels, model.labels_)
        }
    print_results(scores)
    print(f"Best model: {get_best_model(scores)}")


def get_best_model(scores):
    best_score = -float("inf")
    best_model = None

    for name, model_scores in scores.items():
        score = sum(model_scores.values()) / len(model_scores)
        if score > best_score:
            best_score = score
            best_model = name

    return best_model


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


def read_csv_of_regions(df_path, regions, k, preprocess):
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
    if preprocess == 'normalize':
        return normalize_df(df)
    elif preprocess == 'standardize':
        return standardize_df(df)
    else:
        raise ValueError("Error: preprocess must be either 'normalize' or 'standardize'.")


def normalize_df(df):
    print("\tNormalizing data...")
    normalizer = Normalizer()
    columns_sum_zero = df.columns[(df.sum() == 0)]
    order = df.columns
    df = df.drop(columns=columns_sum_zero)
    df[df.columns[3:]] = normalizer.fit_transform(df[df.columns[3:]])
    to_merge = pd.DataFrame(columns=columns_sum_zero, index=df.index)
    to_merge[:] = 0
    df = pd.concat([df, to_merge], axis=1, copy=False)
    return df[order]


def standardize_df(df):
    print("\tStandardizing data...")
    scalar = StandardScaler()
    df[df.columns[3:]] = scalar.fit_transform(df[df.columns[3:]])
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
            if points == result[0]:
                result.append(classifier)
            else:
                break
    return result


def run_models(df_path, level, method, max_sample_size_per_level: int, k, random_state=42):
    if method not in ['clustering', 'classifiers']:
        raise ValueError("Error: method must be either 'cluster' or 'classifiers'.")
    if max_sample_size_per_level < 1:
        raise ValueError("Error: max_sample_size_per_level must be an integer greater than 0.")
    print("Reading CSV...")
    print("\tSampling regions...")
    sampled_regions = get_sampled_regions(df_path, level, max_sample_size_per_level, random_state)
    print("\tReading data...")
    df = read_csv_of_regions(df_path, sampled_regions, k, "normalize" if method == "classifiers" else "standardize")
    y, X = get_y_and_X(df, level)
    print("Sample length: ", len(y))
    print("Sample's classes: ", dict(y.value_counts()))
    if 'sequence' in X.columns:
        X.drop(columns=['sequence'], inplace=True)
    if method == 'clustering':
        print("Clustering...")
        clustering(X, y, random_state)
    else:
        print("Running classifiers...")
        results = get_classifiers_results_with_k_fold(X, y, random_state)
        print_results(results)
        print("Best classifier(s):", get_best_classifier(results))
        print("Temp best: ", get_best_model(results))
    print("Done.")


def main():
    run_models(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))


if __name__ == "__main__":
    main()
