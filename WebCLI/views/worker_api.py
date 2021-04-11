from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import Metrics, Average_history, Accuracy_history
from django.utils import timezone
import json
from WebMark.settings import API_KEY


def as_analyzed_results(result):
    metrics = Metrics.objects.get(pk=result["metrics_id"])
    metrics.qubit_count = result["qubit_count"]
    metrics.timestamp = timezone.now()
    metrics.gate_depth = result["gate_depth"]
    metrics.average_iterations = result["average_iterations"]
    metrics.success_rate = result["success_rate"]
    return metrics


def as_average_history(result):
    histories = result["average_history"]
    for i in range(len(histories)):
        average_history = Average_history(
            analyzed_results=Metrics.objects.get(pk=result["metrics_id"]),
            data=histories[i],
            iteration_number=i)
        average_history.save()
    return average_history


def as_accuracy_history(result):
    histories = result["accuracy_history"]
    for i in range(len(histories)):
        accuracy_history = Accuracy_history(
            analyzed_results=Metrics.objects.get(pk=result["metrics_id"]),
            data=histories[i],
            iteration_number=i)
        accuracy_history.save()
    return accuracy_history


def has_permission(request):
    token = request.headers.get("Authorization")
    return token == API_KEY


@csrf_exempt
def handle_result(request):
    if not has_permission(request):
        print("ACCESS DENIED")
        return HttpResponse("ok")
    analyzed_results = json.loads(request.POST["data"], object_hook=as_analyzed_results)
    analyzed_results.save()
    avg_history_results = json.loads(request.POST["data"], object_hook=as_average_history)
    avg_history_results.save()
    avg_accuracy_results = json.loads(request.POST["data"], object_hook=as_accuracy_history)
    avg_accuracy_results.save()
    return HttpResponse("ok")
