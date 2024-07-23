from django.conf.urls import url
from django.urls import include, path
from . import views_satu_sehat
from . import bridge_satu_sehat

urlpatterns = [
    url(
        r"^views_satu_sehat/",
        include(
            [
                url(r"^$", views_satu_sehat.getToken, name="getToken"),
                url(r"^getOrganization", views_satu_sehat.getOrganization),
                url(
                    r"^getOrganizationInternet",
                    views_satu_sehat.getOrganizationInternet,
                ),
                url(r"^getIHSPatientNumber", views_satu_sehat.getIHSPatientNumber),
                url(r"^getIHSPatientName", views_satu_sehat.getIHSPatientName),
                url(r"^getidKelurahan", views_satu_sehat.getidKelurahan),
                url(
                    r"^getIHSPatientNumberNorm",
                    views_satu_sehat.getIHSPatientNumberNorm,
                ),
                url(r"^saveOrganization", views_satu_sehat.saveOrganization),
                url(r"^savePatient", views_satu_sehat.savePatient),
                url(
                    r"^saveEncounterKunjungan", views_satu_sehat.saveEncounterKunjungan
                ),
                url(
                    r"^updateEncounterKunjungan",
                    views_satu_sehat.updateEncounterKunjungan,
                ),
                url(
                    r"^saveLocationPoli",
                    views_satu_sehat.saveLocationPoli,
                ),
                url(
                    r"^getLocationPoli",
                    views_satu_sehat.getLocationPoli,
                ),
                url(
                    r"^getLocationorganization",
                    views_satu_sehat.getLocationorganization,
                ),
                url(
                    r"^savePractitionerDokter",
                    views_satu_sehat.savePractitionerDokter,
                ),
                url(
                    r"^getPractitionerDokter",
                    views_satu_sehat.getPractitionerDokter,
                ),
                url(
                    r"^greeting",
                    views_satu_sehat.greeting,
                ),
                url(
                    r"^saveConditionICD10",
                    views_satu_sehat.saveConditionICD10,
                ),
                url(r"^getCondition", views_satu_sehat.getCondition),
                url(r"^getConditions", views_satu_sehat.getConditions),
                url(r"^getOrganization", views_satu_sehat.getOrganization),
                url(r"^getLokasi", views_satu_sehat.getLokasi),
                url(r"^getHistoryPasien", views_satu_sehat.getHistoryPasien),
                url(r"^getUrlKYC", views_satu_sehat.getUrlKYC),
                # SERVER INDO
                url(
                    r"^SrvIndoSaveOrganization",
                    views_satu_sehat.saveOrganization_SrvIndo,
                ),
                url(
                    r"^SrvIndoSaveLocationPoli",
                    views_satu_sehat.SrvIndoSaveLocationPoli,
                ),
                url(
                    r"^SrvIndoSavePractitionerDokter",
                    views_satu_sehat.savePractitionerDokter_SrvIndo,
                ),
                url(
                    r"^SrvIndoGetUrlKYC",
                    views_satu_sehat.SrvIndogetUrlKYC,
                ),
            ]
        ),
    ),
    url(
        r"^bridge_satu_sehat/",
        include(
            [
                url(
                    r"^$", bridge_satu_sehat.satu_sehat_bridge, name="satu_sehat_bridge"
                ),
                url(r"^getToken", bridge_satu_sehat.getToken, name="getToken"),
                url(
                    r"^proses_satu_sehat",
                    bridge_satu_sehat.proses_satu_sehat,
                    name="proses_satu_sehat",
                ),
                url(
                    r"^SrvIndoProses_satu_sehat",
                    bridge_satu_sehat.SrvIndoProses_satu_sehat,
                    name="SrvIndoProses_satu_sehat",
                ),
            ]
        ),
    ),
]
