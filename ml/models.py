from django.db import models
from projects.models import Project
from datasets.models import Dataset


class MLResult(models.Model):
    TASK_CHOICES = [
        ('regression', 'Regression'),
        ('classification', 'Classification'),
        ('clustering', 'Clustering'),
    ]
    MODEL_CHOICES = [
        ('linear_regression', 'Linear Regression'),
        ('ridge', 'Ridge Regression'),
        ('lasso', 'Lasso Regression'),
        ('decision_tree_reg', 'Decision Tree (Regression)'),
        ('random_forest_reg', 'Random Forest (Regression)'),
        ('logistic_regression', 'Logistic Regression'),
        ('decision_tree_cls', 'Decision Tree (Classification)'),
        ('random_forest_cls', 'Random Forest (Classification)'),
        ('svm_cls', 'SVM (Classification)'),
        ('knn_cls', 'KNN (Classification)'),
        ('kmeans', 'K-Means Clustering'),
        ('dbscan', 'DBSCAN Clustering'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ml_results')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='ml_results')
    task_type = models.CharField(max_length=20, choices=TASK_CHOICES)
    model_name = models.CharField(max_length=30, choices=MODEL_CHOICES)
    input_columns = models.JSONField(default=list)
    output_column = models.CharField(max_length=200, blank=True)
    parameters = models.JSONField(default=dict)
    metrics = models.JSONField(default=dict)
    predictions = models.JSONField(default=list)
    chart_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_model_name_display()} on {self.dataset.name}'
