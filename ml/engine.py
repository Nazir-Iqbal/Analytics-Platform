import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    silhouette_score,
)


REGRESSION_MODELS = {
    'linear_regression': LinearRegression,
    'ridge': Ridge,
    'lasso': Lasso,
    'decision_tree_reg': DecisionTreeRegressor,
    'random_forest_reg': RandomForestRegressor,
}

CLASSIFICATION_MODELS = {
    'logistic_regression': LogisticRegression,
    'decision_tree_cls': DecisionTreeClassifier,
    'random_forest_cls': RandomForestClassifier,
    'svm_cls': SVC,
    'knn_cls': KNeighborsClassifier,
}

CLUSTERING_MODELS = {
    'kmeans': KMeans,
    'dbscan': DBSCAN,
}


def suggest_models(df, target_column=None):
    suggestions = []
    if target_column:
        if df[target_column].dtype in ['float64', 'int64'] and df[target_column].nunique() > 20:
            suggestions = [
                {'task': 'regression', 'model': 'linear_regression', 'reason': 'Continuous target variable'},
                {'task': 'regression', 'model': 'random_forest_reg', 'reason': 'Good for complex patterns'},
            ]
        else:
            suggestions = [
                {'task': 'classification', 'model': 'logistic_regression', 'reason': 'Categorical target variable'},
                {'task': 'classification', 'model': 'random_forest_cls', 'reason': 'Good for complex patterns'},
            ]
    else:
        suggestions = [
            {'task': 'clustering', 'model': 'kmeans', 'reason': 'No target variable specified'},
        ]
    return suggestions


def run_regression(df, input_columns, output_column, model_name, params=None):
    X = df[input_columns].copy()
    y = df[output_column].copy()

    for col in X.select_dtypes(include='object').columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))

    X = X.fillna(X.mean())
    y = y.fillna(y.mean())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model_class = REGRESSION_MODELS[model_name]
    model = model_class(**(params or {}))
    model.fit(X_train_scaled, y_train)
    predictions = model.predict(X_test_scaled)

    metrics = {
        'mse': round(float(mean_squared_error(y_test, predictions)), 4),
        'rmse': round(float(np.sqrt(mean_squared_error(y_test, predictions))), 4),
        'mae': round(float(mean_absolute_error(y_test, predictions)), 4),
        'r2': round(float(r2_score(y_test, predictions)), 4),
    }

    chart_data = {
        'actual_vs_predicted': {
            'actual': y_test.tolist()[:200],
            'predicted': predictions.tolist()[:200],
        },
        'residuals': (y_test.values - predictions).tolist()[:200],
    }

    return metrics, predictions.tolist()[:500], chart_data


def run_classification(df, input_columns, output_column, model_name, params=None):
    X = df[input_columns].copy()
    y = df[output_column].copy()

    le_y = LabelEncoder()
    y = le_y.fit_transform(y.astype(str))

    for col in X.select_dtypes(include='object').columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))

    X = X.fillna(X.mean())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model_class = CLASSIFICATION_MODELS[model_name]
    model = model_class(**(params or {}))
    model.fit(X_train_scaled, y_train)
    predictions = model.predict(X_test_scaled)

    avg_method = 'weighted' if len(set(y_test)) > 2 else 'binary'
    metrics = {
        'accuracy': round(float(accuracy_score(y_test, predictions)), 4),
        'precision': round(float(precision_score(y_test, predictions, average=avg_method, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, predictions, average=avg_method, zero_division=0)), 4),
        'f1': round(float(f1_score(y_test, predictions, average=avg_method, zero_division=0)), 4),
    }

    classes = le_y.classes_.tolist()
    chart_data = {
        'classes': classes,
        'actual': [int(v) for v in y_test.tolist()[:200]],
        'predicted': [int(v) for v in predictions.tolist()[:200]],
        'class_labels': classes,
    }

    return metrics, predictions.tolist()[:500], chart_data


def run_clustering(df, input_columns, model_name, params=None):
    X = df[input_columns].copy()

    for col in X.select_dtypes(include='object').columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))

    X = X.fillna(X.mean())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    default_params = {}
    if model_name == 'kmeans':
        default_params = {'n_clusters': params.get('n_clusters', 3), 'random_state': 42}
    elif model_name == 'dbscan':
        default_params = {'eps': params.get('eps', 0.5), 'min_samples': params.get('min_samples', 5)}

    model_class = CLUSTERING_MODELS[model_name]
    model = model_class(**default_params)
    labels = model.fit_predict(X_scaled)

    metrics = {}
    n_labels = len(set(labels)) - (1 if -1 in labels else 0)
    if n_labels >= 2:
        metrics['silhouette_score'] = round(float(silhouette_score(X_scaled, labels)), 4)
    metrics['n_clusters'] = n_labels

    chart_data = {
        'labels': labels.tolist()[:500],
        'x': X_scaled[:500, 0].tolist() if X_scaled.shape[1] >= 1 else [],
        'y': X_scaled[:500, 1].tolist() if X_scaled.shape[1] >= 2 else [],
    }

    return metrics, labels.tolist()[:500], chart_data
