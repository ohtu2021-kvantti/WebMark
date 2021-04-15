from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import Metrics, Average_history, Accuracy_history
from django.utils import timezone
import json


def as_analyzed_results(result):
    metrics = Metrics.objects.get(pk=result["metrics_id"])
    metrics.qubit_count = result["qubit_count"]
    metrics.timestamp = timezone.now()
    metrics.gate_depth = result["gate_depth"]
    metrics.average_iterations = result["average_iterations"]
    metrics.success_rate = result["success_rate"]
    return metrics


def as_history(result):
    avg_histories = result["average_history"]
    avg_existing_history = Average_history.objects.filter(analyzed_results=result["metrics_id"])
    acc_histories = result["accuracy_history"]
    acc_existing_history = Accuracy_history.objects.filter(analyzed_results=result["metrics_id"])

    if len(avg_existing_history) > 0 & len(acc_existing_history) > 0:
        history = avg_existing_history[0]
        return history
    if len(avg_existing_history) < 1:
        for i in range(len(avg_histories)):
            history = Average_history(
                analyzed_results=Metrics.objects.get(pk=result["metrics_id"]),
                data=avg_histories[i],
                iteration_number=i+1)
            history.save()

    if len(acc_existing_history) < 1:
        for i in range(len(acc_histories)):
            history = Accuracy_history(
                analyzed_results=Metrics.objects.get(pk=result["metrics_id"]),
                data=acc_histories[i],
                iteration_number=i+1)
            history.save()

    return history


# TODO: set this route to accept from workers only
@csrf_exempt
def handle_result(request):
    analyzed_results = json.loads(request.POST["data"], object_hook=as_analyzed_results)
    analyzed_results.save()
    history_results = json.loads(request.POST["data"], object_hook=as_history)
    history_results.save()
    return HttpResponse("ok")
