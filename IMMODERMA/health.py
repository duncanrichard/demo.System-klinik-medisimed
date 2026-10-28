import logging

from django.db import DatabaseError, connection
from django.http import JsonResponse


logger = logging.getLogger(__name__)


def health(request):
    return JsonResponse({"status": "ok"})


def database_health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        logger.exception("Database health check failed")
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "database": "available"})

