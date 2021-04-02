from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import Analyzed_results
from django.utils import timezone
import json


def as_analyzed_results(result):
    return Analyzed_results(
        metrics_id=result["metrics_id"],
        timestamp=timezone.now(),
        qubit_count=result["qubit_count"],
        gate_depth=result["gate_depth"],
        average_iterations=result["average_iterations"],
        success_rate=result["success_rate"]
    )


# TODO: set this route to accept from workers only
@csrf_exempt
def handle_result(request):
    analyzed_results = json.loads(request.POST["data"], object_hook=as_analyzed_results)
    analyzed_results.save()
    return HttpResponse("ok")
