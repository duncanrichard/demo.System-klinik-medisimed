from django.conf.urls import url
from django.urls import include, path
from . import emr_perawat
from dashboard import data_pasien

urlpatterns = [
    url(
        r"^emr_perawat/",
        include(
            [
                url(r"^$", emr_perawat.emr_perawat, name="emr_perawat"),
                url(r"^get-pasien-rj", emr_perawat.getPasienRJ, name="getPasienRJ"),
                url(
                    r"^getPanggilAntrian",
                    emr_perawat.getPanggilAntrian,
                    name="getPanggilAntrian",
                ),
                url(
                    r"^panggilAntrianPendaftaran",
                    emr_perawat.panggilAntrianPendaftaran,
                    name="panggilAntrianPendaftaran",
                ),
                url(r"^SP_ALERGI", emr_perawat.SP_ALERGI),
                url(r"^OpenDiagnosaGigiVisual", emr_perawat.OpenDiagnosaGigiVisual),
                url(r"^generateResepTXT", emr_perawat.generateResepTXT),
                url(r"^getIdDataDiagnosa", emr_perawat.getIdDataDiagnosa),
                url(r"^getDataDiagnosa", emr_perawat.getDataDiagnosa),
                url(r"^Openpenyakit", emr_perawat.Openpenyakit),
                url(r"^findStatusKasus", emr_perawat.findStatusKasus),
                url(r"^findStatusDiagnosaKlaim", emr_perawat.findStatusDiagnosaKlaim),
                url(
                    r"^findStatusDiagnosaKlaimAwal",
                    emr_perawat.findStatusDiagnosaKlaimAwal,
                ),
                url(r"^save_assesment", emr_perawat.save_assesment),
                url(r"^save_cuti", emr_perawat.save_cuti),
                url(r"^save_cppt", emr_perawat.save_cppt),
                url(
                    r"^printSuratKeteranganSehat", emr_perawat.printSuratKeteranganSehat
                ),
                url(r"^printSuratRTW", emr_perawat.printSuratRTW),
                url(r"^printSuratFTW", emr_perawat.printSuratFTW),
                url(
                    r"^printSuratKeteranganDokter",
                    emr_perawat.printSuratKeteranganDokter,
                ),
                url(
                    r"^printSuratKeteranganDokter",
                    emr_perawat.printSuratKeteranganDokter,
                ),
                url(r"^printSuratKematianKlinik", emr_perawat.printSuratKematianKlinik),
                url(
                    r"^printSuratPenolakanTindakanKedokteran",
                    emr_perawat.printSuratPenolakanTindakanKedokteran,
                ),
                url(
                    r"^printSuratPersetujuanTindakanKedokteran",
                    emr_perawat.printSuratPersetujuanTindakanKedokteran,
                ),
                url(
                    r"^printSuratRujukanPCAREBPJS",
                    emr_perawat.printSuratRujukanPCAREBPJS,
                ),
                url(
                    r"^detailResep",
                    emr_perawat.detailResep,
                ),
                url(
                    r"^getIdDataBarang",
                    emr_perawat.getIdDataBarang,
                ),
                url(
                    r"^getDataBarang",
                    emr_perawat.getDataBarang,
                ),
                url(
                    r"^getHistoryBarang",
                    emr_perawat.getHistoryBarang,
                ),
                url(
                    r"^crudResepRJ",
                    emr_perawat.crudResepRJ,
                ),
                url(
                    r"^deleteEresep",
                    emr_perawat.deleteEresep,
                ),
                url(
                    r"^DaftardetailResep",
                    emr_perawat.DaftardetailResep,
                ),
                url(
                    r"^crudDaftarResep",
                    emr_perawat.crudDaftarResep,
                ),
                url(
                    r"^pickerDaftarResep",
                    emr_perawat.pickerDaftarResep,
                ),
                url(
                    r"^deleteItemPaketResep",
                    emr_perawat.deleteItemPaketResep,
                ),
                url(r"^getHistoricalBPJSpasien", emr_perawat.getHistoricalBPJSpasien),
                url(r"^cekIcare", emr_perawat.cekIcare),
                url(r"^crudBridgingBPJSLab", emr_perawat.crudBridgingBPJSLab),
                url(r"^getBPJSMCU", emr_perawat.getBPJSMCU),
                url(r"^deleteBPJSMCU", emr_perawat.deleteBPJSMCU),
                url(r"^getHistoricalsurvei", emr_perawat.getHistoricalsurvei),
                url(
                    r"^getRiwayatPemeriksaanByNORMDetail",
                    emr_perawat.getRiwayatPemeriksaanByNORMDetail,
                ),
                url(
                    r"^getriwayat",
                    emr_perawat.getriwayat,
                ),
                url(
                    r"^getjkn",
                    emr_perawat.getjkn,
                ),
                url(
                    r"^ftw/",
                    include(
                        [
                            # url(r'^$', emr_perawat.page_elab, name='emrrj_page_elab'),
                            url(r"^save", emr_perawat.save_ftw, name="emr_save_ftw"),
                            url(r"^get", emr_perawat.get_ftw, name="emrrj_get_ftw"),
                        ]
                    ),
                ),
                url(r"^printResepDoktermanual", emr_perawat.printResepDoktermanual),
                url(r"^printResepDokter", emr_perawat.printResepDokter),
                url(r"^printCPPT", emr_perawat.printCPPT),
                url(r"^getPasien", data_pasien.getPasien),
                url(r"^getDataKunjunganPasien", emr_perawat.getDataKunjunganPasien),
            ]
        ),
    ),
]
