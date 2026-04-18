import json
import functools
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from accounts.models import Profile
from projects.models import Project
from datasets.models import Dataset
from ml.models import MLResult


def api_key_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        api_key = request.headers.get('X-API-Key', '') or request.GET.get('api_key', '')
        if not api_key:
            return JsonResponse({'error': 'API key required'}, status=401)
        try:
            profile = Profile.objects.select_related('user').get(api_key=api_key)
            request.api_user = profile.user
        except Profile.DoesNotExist:
            return JsonResponse({'error': 'Invalid API key'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@api_key_required
@require_http_methods(['GET'])
def api_projects(request):
    projects = Project.objects.filter(user=request.api_user).values('id', 'name', 'description', 'created_at')
    return JsonResponse({'projects': list(projects)}, json_dumps_params={'default': str})


@api_key_required
@require_http_methods(['GET'])
def api_datasets(request, project_pk):
    project = Project.objects.filter(pk=project_pk, user=request.api_user).first()
    if not project:
        return JsonResponse({'error': 'Project not found'}, status=404)
    datasets = Dataset.objects.filter(project=project).values('id', 'name', 'rows', 'columns', 'column_names', 'uploaded_at')
    return JsonResponse({'datasets': list(datasets)}, json_dumps_params={'default': str})


@api_key_required
@require_http_methods(['GET'])
def api_results(request, project_pk):
    project = Project.objects.filter(pk=project_pk, user=request.api_user).first()
    if not project:
        return JsonResponse({'error': 'Project not found'}, status=404)
    results = MLResult.objects.filter(project=project).values(
        'id', 'task_type', 'model_name', 'metrics', 'input_columns', 'output_column', 'created_at'
    )
    return JsonResponse({'results': list(results)}, json_dumps_params={'default': str})


@api_key_required
@require_http_methods(['GET'])
def api_result_detail(request, pk):
    result = MLResult.objects.filter(pk=pk, project__user=request.api_user).first()
    if not result:
        return JsonResponse({'error': 'Result not found'}, status=404)
    data = {
        'id': result.pk,
        'task_type': result.task_type,
        'model_name': result.model_name,
        'metrics': result.metrics,
        'predictions': result.predictions[:100],
        'chart_data': result.chart_data,
        'input_columns': result.input_columns,
        'output_column': result.output_column,
    }
    return JsonResponse(data)
