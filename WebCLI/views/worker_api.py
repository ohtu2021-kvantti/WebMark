from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import Metrics, Average_history
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

def as_average_history(result):
    histories = result["average_history"]
    for i in range(len(histories)):
        average_history = Average_history(
            analyzed_results=Metrics.objects.get(pk=result["metrics_id"]),
            data=histories[i],
            iteration_number=i)
        average_history.save()
    return average_history

# TODO: set this route to accept from workers only
@csrf_exempt
def handle_result(request):
    analyzed_results = json.loads(request.POST["data"], object_hook=as_analyzed_results)
    analyzed_results.save()
    avg_history_results = json.loads(request.POST["data"], object_hook=as_average_history)
    avg_history_results.save()
    return HttpResponse("ok")
