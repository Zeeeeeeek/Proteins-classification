import sys

import pandas as pd
from sklearn import metrics
from sklearn.cluster import AgglomerativeClustering
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelBinarizer
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

"""
Usage: python models.py <path_to_csv> <level> <method> <max_sample_size_per_level>
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


def get_classifiers():
    names = [
        "K Nearest Neighbors",
        "SVM",
        "Decision Tree",
        "Random Forest",
        "Random Forest Log Loss",
        # "Neural Net",
        "Naive Bayes"
    ]
    classifiers = [
        KNeighborsClassifier(),
        SVC(random_state=RANDOM_STATE),
        DecisionTreeClassifier(random_state=RANDOM_STATE),
        RandomForestClassifier(random_state=RANDOM_STATE),
        RandomForestClassifier(random_state=RANDOM_STATE, criterion='log_loss'),
        # MLPClassifier(random_state=RANDOM_STATE, max_iter=1000),
        GaussianNB()
    ]
    return names, classifiers


def get_classifiers_results(X, y):
    names, classifiers = get_classifiers()
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
        try:
            lb = LabelBinarizer()
            lb.fit(y_test)
            y_test_lb = lb.transform(y_test)
            y_pred_lb = lb.transform(y_pred)
            results[classifier_name]["AUC-ROC"] = metrics.roc_auc_score(y_test_lb, y_pred_lb, average='weighted',
                                                                        multi_class='ovr')
        except ValueError:
            results[classifier_name]["AUC-ROC"] = None
    return results


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


def print_k_fold_results(X, y):
    cv = KFold(n_splits=10, random_state=RANDOM_STATE, shuffle=True)
    names, classifiers = get_classifiers()
    print("K-Fold Cross Validation Results:")
    for index, classifier in enumerate(classifiers):
        print("=" * 30)
        print(names[index])
        scores = cross_val_score(classifier, X, y, cv=cv, scoring='accuracy')
        print(f"Accuracy: {scores.mean():.4f}")
        print()


def print_cluster_metrics(labels_true, labels_pred, method: str):
    print("=" * 30)
    print(f"Method: {method}")
    print("\tRand_score", metrics.rand_score(labels_true, labels_pred))
    print("\tadjusted_rand_score", metrics.adjusted_rand_score(labels_true, labels_pred))
    print("\tHomogeneity_score", metrics.homogeneity_score(labels_true, labels_pred))
    print("\tCompleteness_score", metrics.completeness_score(labels_true, labels_pred))
    print("\tfowlkes_mallows_score", metrics.fowlkes_mallows_score(labels_true, labels_pred))


def cluster(X, label_dict):
    model = AgglomerativeClustering(n_clusters=len(label_dict), linkage='single')
    labels_pred = model.fit_predict(X)
    print_cluster_metrics(label_dict, labels_pred, "single")
    model = AgglomerativeClustering(n_clusters=len(label_dict), linkage='complete')
    labels_pred = model.fit_predict(X)
    print_cluster_metrics(label_dict, labels_pred, "complete")
    model = AgglomerativeClustering(n_clusters=len(label_dict), linkage='average')
    labels_pred = model.fit_predict(X)
    print_cluster_metrics(label_dict, labels_pred, "average")


def get_sampled_regions(df_path, level: str, sample_size: int):
    df = pd.read_csv(df_path, usecols=["region_id", "class_topology_fold_clan"],
                     dtype={"region_id": str, "class_topology_fold_clan": str})
    df['label'] = get_y_from_df_and_level(df, level)
    counter = df['label'].value_counts().to_dict()
    for key, count in counter.items():
        if count > sample_size:
            counter[key] = sample_size
    return df.groupby('label').apply(lambda x: x.sample(n=counter[x.name]), include_groups=False)['region_id'].tolist()


def read_csv_of_regions(df_path, regions):
    index = 0
    rows = []
    reg_copy = regions.copy()
    with open(df_path, "r") as file:
        for line in file:
            if index == 0:
                columns = line.strip().split(",")
                index += 1
            if line.strip().split(",")[0] in reg_copy:
                split = line.strip().split(",")
                row = []
                column_index = 0
                for s in split:
                    if s == '':
                        row.append(0)
                        continue
                    if column_index > 2:
                        row.append(int(s))
                    else:
                        row.append(s)
                        column_index += 1
                rows.append(row)
                reg_copy.remove(line.strip().split(",")[0])
            if len(reg_copy) == 0:
                break
    return pd.DataFrame(rows, columns=columns)


def run_models(df_path, level, method, max_sample_size_per_level):
    if method not in ['cluster', 'classifiers']:
        raise ValueError("Error: method must be either 'cluster' or 'classifiers'.")
    if max_sample_size_per_level < 1 or not isinstance(max_sample_size_per_level, int):
        raise ValueError("Error: max_sample_size_per_level must be an integer greater than 0.")
    print("Reading CSV...")
    print("\tSampling regions...")
    sampled_regions = get_sampled_regions(df_path, level, max_sample_size_per_level)
    print("\tReading data...")
    df = read_csv_of_regions(df_path, sampled_regions)
    y = get_y_from_df_and_level(df, level)
    X = df.drop(columns=["class_topology_fold_clan", "sequence", "region_id"])
    print("Data read.")
    if method == 'cluster':
        print("Clustering...")
        cluster(X, y)
    else:
        print("Running classifiers...")
        results = get_classifiers_results(X, y)
        print_results(results)
        print_k_fold_results(X, y)
    print("Done.")


def main():
    run_models(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))


if __name__ == "__main__":
    main()
