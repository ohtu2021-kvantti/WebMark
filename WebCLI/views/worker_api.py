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
    # tässä joku ongelma
    average_history = Average_history.objects.get(pk= result["metrics_id"])
    print("tÄLLÄISTÄ " + result["average_history"])
    average_history.data = result["average_history"]
    return average_history

# TODO: set this route to accept from workers only
@csrf_exempt
def handle_result(request):
    analyzed_results = json.loads(request.POST["data"], object_hook=as_analyzed_results)
    analyzed_results.save()
    average_history = json.loads(request.POST["data"], object_hook=as_average_history)
    average_history.save()
    return HttpResponse("ok")
