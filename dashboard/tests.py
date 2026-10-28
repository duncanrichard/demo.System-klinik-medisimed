from unittest.mock import patch
from datetime import date

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, SimpleTestCase

from . import kasir_rj, pemasukan_realtime


def request_with_session(path, data=None):
    request = RequestFactory().get(path, data=data or {})
    middleware = SessionMiddleware(lambda current_request: None)
    middleware.process_request(request)
    return request


class KasirPageTests(SimpleTestCase):
    @patch("dashboard.kasir_rj.Globals.isLogin", return_value=False)
    def test_anonymous_request_redirects_without_loading_database_menus(self, _):
        request = request_with_session("/kasir_rj/")

        response = kasir_rj.kasir_rj(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login")

    @patch("dashboard.kasir_rj.Globals.getMenubars", return_value=[])
    @patch("dashboard.kasir_rj.Globals.getNavbars", return_value=[])
    @patch("dashboard.kasir_rj.Globals.isLogin", return_value=True)
    def test_authenticated_page_renders_all_case_sensitive_includes(
        self, _is_login, _navbars, _menubars
    ):
        request = request_with_session("/kasir_rj/")
        request.session.update(
            {
                "user_priv": "TEST",
                "kdCabang": "001",
                "nama_cabang": "Klinik Test",
                "kota_cabang": "Jakarta",
                "par_MTH": "10",
                "par_TAHUNYR": "2026",
            }
        )

        response = kasir_rj.kasir_rj(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Cache-Control"], "no-cache, no-store, max-age=0, must-revalidate"
        )


class KasirVoucherTests(SimpleTestCase):
    @patch("dashboard.kasir_rj.Globals.getDataQuery", return_value=[])
    def test_voucher_lookup_binds_voucher_number(self, query):
        request = request_with_session(
            "/kasir_rj/getVoucherPay",
            {"tipe": "idvoucher", "novoucher": "V-001"},
        )

        response = kasir_rj.getVoucherPay(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(query.call_args.args[1], ["V-001"])

    def test_voucher_lookup_rejects_missing_voucher_number(self):
        request = request_with_session(
            "/kasir_rj/getVoucherPay", {"tipe": "idvoucher"}
        )

        response = kasir_rj.getVoucherPay(request)

        self.assertEqual(response.status_code, 400)


class PemasukanRealtimeTests(SimpleTestCase):
    def _authenticated_request(self, path, data=None):
        request = request_with_session(path, data)
        request.session.update(
            {
                "user_priv": "TEST",
                "kdCabang": "001",
                "kota_cabang": "Jakarta",
                "nama_cabang": "Klinik Test",
                "par_MTH": "10",
                "par_TAHUNYR": "2026",
            }
        )
        return request

    @patch("dashboard.pemasukan_realtime.Globals.isLogin", return_value=False)
    def test_page_requires_login(self, _is_login):
        response = pemasukan_realtime.pemasukan_realtime(
            request_with_session("/pemasukan_realtime/")
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login")

    @patch("dashboard.pemasukan_realtime.Globals.getSeparator", return_value=[])
    @patch("dashboard.pemasukan_realtime.Globals.getMenubars", return_value=[])
    @patch("dashboard.pemasukan_realtime.Globals.getNavbars", return_value=[])
    @patch("dashboard.pemasukan_realtime.Globals.isLogin", return_value=True)
    def test_page_renders(self, _is_login, _navbars, _menubars, _separator):
        response = pemasukan_realtime.pemasukan_realtime(
            self._authenticated_request("/pemasukan_realtime/")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pemasukan Realtime")

    @patch("dashboard.pemasukan_realtime.Globals.getDataQuery")
    @patch("dashboard.pemasukan_realtime.Globals.isLogin", return_value=True)
    def test_data_uses_parameterized_branch_and_day_range(self, _is_login, query):
        query.return_value = [{"TUNAI": 10000, "BANK": 5000, "PIUTANG": 0, "JAMINAN": 0, "VOUCHER": 0}]

        response = pemasukan_realtime.data(
            self._authenticated_request("/pemasukan_realtime/data/", {"tanggal": "2026-10-27"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(query.call_args.args[1], ["001", date(2026, 10, 27), date(2026, 10, 28)])
        self.assertJSONEqual(response.content, {"tanggal": "2026-10-27", "data": query.return_value, "ringkasan": {"TUNAI": "10000", "BANK": "5000", "PIUTANG": "0", "JAMINAN": "0", "VOUCHER": "0", "TOTAL": "15000"}})

    @patch("dashboard.pemasukan_realtime.Globals.getDataQuery", return_value=[])
    @patch("dashboard.pemasukan_realtime.Globals.isLogin", return_value=True)
    def test_export_returns_xlsx(self, _is_login, _query):
        response = pemasukan_realtime.export(
            self._authenticated_request("/pemasukan_realtime/export/", {"tanggal": "2026-10-27"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertTrue(response.content.startswith(b"PK"))
