import json
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datasets.models import Dataset
from projects.models import Project
from .models import MLResult
from .engine import (
    run_regression, run_classification, run_clustering,
    suggest_models, REGRESSION_MODELS, CLASSIFICATION_MODELS, CLUSTERING_MODELS,
)


@login_required
def model_select(request, dataset_pk):
    dataset = get_object_or_404(Dataset, pk=dataset_pk, project__user=request.user)
    df = pd.read_csv(dataset.file.path)
    columns = list(df.columns)
    numeric_cols = list(df.select_dtypes(include='number').columns)
    categorical_cols = list(df.select_dtypes(include='object').columns)

    regression_models = [(k, v.__name__) for k, v in REGRESSION_MODELS.items()]
    classification_models = [(k, v.__name__) for k, v in CLASSIFICATION_MODELS.items()]
    clustering_models = [(k, v.__name__) for k, v in CLUSTERING_MODELS.items()]

    return render(request, 'ml/select.html', {
        'dataset': dataset,
        'columns': columns,
        'numeric_cols': numeric_cols,
        'categorical_cols': categorical_cols,
        'regression_models': regression_models,
        'classification_models': classification_models,
        'clustering_models': clustering_models,
    })


@login_required
def model_train(request, dataset_pk):
    dataset = get_object_or_404(Dataset, pk=dataset_pk, project__user=request.user)
    if request.method != 'POST':
        return redirect('ml:select', dataset_pk=dataset.pk)

    task_type = request.POST.get('task_type')
    model_name = request.POST.get('model_name')
    input_columns = request.POST.getlist('input_columns')
    output_column = request.POST.get('output_column', '')

    if not input_columns:
        messages.error(request, 'Please select at least one input column.')
        return redirect('ml:select', dataset_pk=dataset.pk)

    if task_type in ('regression', 'classification') and not output_column:
        messages.error(request, 'Please select an output column.')
        return redirect('ml:select', dataset_pk=dataset.pk)

    df = pd.read_csv(dataset.file.path)
    params = {}

    if model_name == 'kmeans':
        try:
            params['n_clusters'] = int(request.POST.get('n_clusters', 3))
        except (ValueError, TypeError):
            params['n_clusters'] = 3

    try:
        if task_type == 'regression':
            metrics, predictions, chart_data = run_regression(df, input_columns, output_column, model_name, params)
        elif task_type == 'classification':
            metrics, predictions, chart_data = run_classification(df, input_columns, output_column, model_name, params)
        elif task_type == 'clustering':
            metrics, predictions, chart_data = run_clustering(df, input_columns, model_name, params)
        else:
            messages.error(request, 'Invalid task type.')
            return redirect('ml:select', dataset_pk=dataset.pk)

        result = MLResult.objects.create(
            project=dataset.project,
            dataset=dataset,
            task_type=task_type,
            model_name=model_name,
            input_columns=input_columns,
            output_column=output_column,
            parameters=params,
            metrics=metrics,
            predictions=predictions,
            chart_data=chart_data,
        )
        messages.success(request, 'Model trained successfully!')
        return redirect('ml:result', pk=result.pk)

    except Exception as e:
        messages.error(request, f'Training error: {e}')
        return redirect('ml:select', dataset_pk=dataset.pk)


@login_required
def model_result(request, pk):
    result = get_object_or_404(MLResult, pk=pk, project__user=request.user)
    return render(request, 'ml/result.html', {
        'result': result,
        'metrics_json': json.dumps(result.metrics),
        'chart_data_json': json.dumps(result.chart_data),
        'predictions_json': json.dumps(result.predictions[:100]),
    })


@login_required
def model_compare(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, user=request.user)
    results = project.ml_results.all()
    comparisons = []
    for r in results:
        comparisons.append({
            'id': r.pk,
            'model': r.get_model_name_display(),
            'task': r.get_task_type_display(),
            'dataset': r.dataset.name,
            'metrics': r.metrics,
            'created': r.created_at.isoformat(),
        })
    return render(request, 'ml/compare.html', {
        'project': project,
        'comparisons': comparisons,
        'comparisons_json': json.dumps(comparisons),
    })


@login_required
def model_suggest(request, dataset_pk):
    dataset = get_object_or_404(Dataset, pk=dataset_pk, project__user=request.user)
    target = request.GET.get('target', '')
    df = pd.read_csv(dataset.file.path)
    suggestions = suggest_models(df, target if target else None)
    return JsonResponse({'suggestions': suggestions})


@login_required
def result_delete(request, pk):
    result = get_object_or_404(MLResult, pk=pk, project__user=request.user)
    project_pk = result.project.pk
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Result deleted.')
        return redirect('projects:detail', pk=project_pk)
    return render(request, 'ml/delete_result.html', {'result': result})


@login_required
def result_export(request, pk):
    result = get_object_or_404(MLResult, pk=pk, project__user=request.user)
    data = {
        'model': result.get_model_name_display(),
        'task': result.get_task_type_display(),
        'dataset': result.dataset.name,
        'input_columns': result.input_columns,
        'output_column': result.output_column,
        'metrics': result.metrics,
        'predictions': result.predictions[:100],
        'parameters': result.parameters,
    }
    return JsonResponse(data, json_dumps_params={'indent': 2})
