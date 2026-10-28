from unittest.mock import patch

from django.db import DatabaseError
from django.test import RequestFactory, SimpleTestCase

from .health import database_health, health


class HealthCheckTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/health/")

    def test_liveness_does_not_require_database(self):
        response = health(self.request)
        self.assertEqual(response.status_code, 200)

    @patch("IMMODERMA.health.connection")
    def test_database_failure_returns_service_unavailable(self, database_connection):
        database_connection.cursor.side_effect = DatabaseError
        response = database_health(self.request)
        self.assertEqual(response.status_code, 503)
