from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# TODO: set this route to accept from workers only
@csrf_exempt
def handle_result(request):
    result = request.POST['result']
    # TODO: figure out which algorithm version this was
    # and update database with verified results
    print(result)
    return HttpResponse("ok")
