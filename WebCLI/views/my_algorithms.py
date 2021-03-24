from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ..models import Algorithm
from .homepage import AlgorithmListView


class MyAlgorithmListView(AlgorithmListView):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(MyAlgorithmListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return Algorithm.objects.filter(user=self.request.user).order_by("name")
