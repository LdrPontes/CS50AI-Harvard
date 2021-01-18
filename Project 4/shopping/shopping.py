import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    raw_data = list()

    labels = list()
    evidences = list()

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile,delimiter=",", )
        for i in reader:
            raw_data.append(i)
        raw_data.pop(0)

    for row in raw_data:
        labels.append(int(row[len(row) - 1] == "TRUE"))
        evidence = list()
        for i in range(17):
            evidence.append(convert_evidences(row[i], i))
        evidences.append(evidence)

    return (evidences, labels)


def convert_evidences(value, position):
    int_positions = [0, 2, 4, 10, 11, 12, 13, 14, 15, 16]
    float_positions = [1, 3, 5, 6, 7, 8, 9]

    if(position in int_positions):
        if(position == 10):
            return int(month_to_int(value))
        if(position == 15):
            return int(value == "Returning_Visitor")
        if(position == 16):
            return int(value == "TRUE")
        return int(value)
    else:
        return float(value)


def month_to_int(month):
    if(month == "Jan"):
        return 0
    if(month == "Feb"):
        return 1
    elif(month == "Mar"):
        return 2
    elif(month == "Apr"):
        return 3
    elif(month == "May"):
        return 4
    elif(month == "June"):
        return 5
    elif(month == "Jul"):
        return 6
    elif(month == "Aug"):
        return 7
    elif(month == "Sep"):
        return 8
    elif(month == "Oct"):
        return 9
    elif(month == "Nov"):
        return 10
    else:
        return 11


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    x_training = [item for item in evidence]
    y_training = [item for item in labels]
    return model.fit(x_training, y_training)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    count_positive = 0
    count_negative = 0

    count_sensitivity = 0
    count_specificity = 0

    for i in range(len(labels)):
        if(labels[i] == 1):
            count_positive += 1
            if(labels[i] == predictions[i]):
                count_sensitivity += 1
        else:
            count_negative += 1
            if(labels[i] == predictions[i]):
                count_specificity += 1

    sensitivity = count_sensitivity / count_positive
    specificity = count_specificity / count_negative

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
