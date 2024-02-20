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
Usage: 


"""
RANDOM_STATE = 42


def get_lambda_from_level(level: str):
    match level:
        case "class":
            return lambda row: row["class_topology_fold_clan"].split(".")[0]
        case "topology":
            return lambda row: row["class_topology_fold_clan"].split(".")[1]
        case "fold":
            return lambda row: row["class_topology_fold_clan"].split(".")[2]
        case "clan":
            return lambda row: row["class_topology_fold_clan"].split(".")[3]
        case "class_topology":
            return lambda row: row["class_topology_fold_clan"].split(".")[0:2]
        case "class_topology_fold":
            return lambda row: row["class_topology_fold_clan"].split(".")[0:3]
        case "class_topology_fold_clan":
            return lambda row: row["class_topology_fold_clan"]
        case _:
            raise ValueError(f"Error: {level} is not a valid level. Please use one of the following: "
                             f"class, topology, fold, clan, class_topology, class_topology_fold, "
                             f"class_topology_fold_clan.")


def classify(df, level):
    y = df.apply(get_lambda_from_level(level), axis=1)
    X = df.drop(columns=["class_topology_fold_clan", "sequence", "region_id"]).fillna(0)
    classifiers = [
        KNeighborsClassifier(),
        SVC(random_state=RANDOM_STATE),
        DecisionTreeClassifier(random_state=RANDOM_STATE),
        RandomForestClassifier(random_state=RANDOM_STATE),
        MLPClassifier(random_state=RANDOM_STATE, max_iter=1000),
        GaussianNB()
    ]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=RANDOM_STATE)
    results = {}
    for classifier in classifiers:
        classifier_name = classifier.__class__.__name__
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
        print("="*30)
        print(classifier)
        print("\nMetrics:")
        for metric, value in met.items():
            print(f"{metric}: {value}")
        print()

def main():
    df = pd.read_csv("../csv/regioni_1_mer.csv")
    print_results(classify(df, "class_topology_fold_clan"))


if __name__ == "__main__":
    main()
