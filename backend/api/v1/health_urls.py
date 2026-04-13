from django.http import JsonResponse
from django.urls import path

from apps.nasa_ingest.circuit import state as circuit_state


def health(_):
    return JsonResponse({"status": "ok", "nasa_circuit": circuit_state()})


urlpatterns = [path("", health, name="health")]
