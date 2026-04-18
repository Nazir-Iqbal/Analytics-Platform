import io
import json
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from projects.models import Project
from .models import Dataset


@login_required
def dataset_upload(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, user=request.user)
    if request.method == 'POST':
        file = request.FILES.get('file')
        name = request.POST.get('name', '').strip()
        if not file:
            messages.error(request, 'Please select a file.')
            return render(request, 'datasets/upload.html', {'project': project})
        if not file.name.endswith('.csv'):
            messages.error(request, 'Only CSV files are supported.')
            return render(request, 'datasets/upload.html', {'project': project})
        if not name:
            name = file.name.rsplit('.', 1)[0]

        try:
            content = file.read()
            df = pd.read_csv(io.BytesIO(content))
            file.seek(0)

            dataset = Dataset.objects.create(
                project=project,
                name=name,
                file=file,
                rows=len(df),
                columns=len(df.columns),
                column_names=list(df.columns),
            )
            messages.success(request, f'Dataset "{dataset.name}" uploaded ({dataset.rows} rows, {dataset.columns} columns).')
            return redirect('datasets:preview', pk=dataset.pk)
        except Exception as e:
            messages.error(request, f'Error reading CSV: {e}')

    return render(request, 'datasets/upload.html', {'project': project})


@login_required
def dataset_preview(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk, project__user=request.user)
    df = pd.read_csv(dataset.file.path)

    stats = {
        'shape': f'{df.shape[0]} rows x {df.shape[1]} columns',
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing': df.isnull().sum().to_dict(),
        'describe': df.describe(include='all').fillna('').to_dict(),
    }

    preview_rows = df.head(50).fillna('').values.tolist()
    columns = list(df.columns)

    return render(request, 'datasets/preview.html', {
        'dataset': dataset,
        'columns': columns,
        'rows': preview_rows,
        'stats': stats,
        'stats_json': json.dumps(stats, default=str),
    })


@login_required
def dataset_stats(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk, project__user=request.user)
    df = pd.read_csv(dataset.file.path)

    stats = {
        'shape': list(df.shape),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing': df.isnull().sum().to_dict(),
        'describe': df.describe(include='all').fillna('').to_dict(),
        'numeric_columns': list(df.select_dtypes(include='number').columns),
        'categorical_columns': list(df.select_dtypes(include='object').columns),
    }
    return JsonResponse(stats)


@login_required
def dataset_handle_missing(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk, project__user=request.user)
    if request.method == 'POST':
        strategy = request.POST.get('strategy', 'drop')
        columns = request.POST.getlist('columns')
        df = pd.read_csv(dataset.file.path)

        if columns:
            subset = columns
        else:
            subset = list(df.columns)

        if strategy == 'drop':
            df = df.dropna(subset=subset)
        elif strategy == 'mean':
            for col in subset:
                if df[col].dtype in ['float64', 'int64']:
                    df[col] = df[col].fillna(df[col].mean())
        elif strategy == 'median':
            for col in subset:
                if df[col].dtype in ['float64', 'int64']:
                    df[col] = df[col].fillna(df[col].median())
        elif strategy == 'mode':
            for col in subset:
                df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else df[col])
        elif strategy == 'zero':
            df[subset] = df[subset].fillna(0)

        df.to_csv(dataset.file.path, index=False)
        dataset.rows = len(df)
        dataset.column_names = list(df.columns)
        dataset.save()
        messages.success(request, f'Missing values handled using "{strategy}" strategy.')
        return redirect('datasets:preview', pk=dataset.pk)

    df = pd.read_csv(dataset.file.path)
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0].to_dict()
    return render(request, 'datasets/handle_missing.html', {
        'dataset': dataset,
        'missing_cols': missing_cols,
    })


@login_required
def dataset_delete(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk, project__user=request.user)
    project_pk = dataset.project.pk
    if request.method == 'POST':
        dataset.file.delete()
        dataset.delete()
        messages.success(request, 'Dataset deleted.')
        return redirect('projects:detail', pk=project_pk)
    return render(request, 'datasets/delete.html', {'dataset': dataset})


@login_required
def dataset_columns(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk, project__user=request.user)
    df = pd.read_csv(dataset.file.path)
    data = {
        'columns': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'numeric_columns': list(df.select_dtypes(include='number').columns),
        'categorical_columns': list(df.select_dtypes(include='object').columns),
    }
    return JsonResponse(data)
