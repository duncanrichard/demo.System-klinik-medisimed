from django.conf.urls import url, include
from . import views_dashboard
from . import views
from . import views_pcare

urlpatterns = [
    url(r'^emr/',include([
        url(r'^$', views.page_cppt, name='emrj_dashboard'),
        url(r'^getNakes', views.getNakes, name='emrj_getNakes'),
        url(r'^data-cppt', views.getDataCPPT, name='emrj_getDataCPPT'),
        url(r'^detail-entry-resep', views.getDetailPasienRJ, name='getDetailPasienRJ'),
        url(r'^get-pasien-rj', views.getPasienRJ, name='getPasienRJ'),
        url(r'^set-session', views.setSession, name='setSession'),
        url(r'^get-data-pasien', views.getDataHistoryPasien, name='getDataHistoryPasien'),
        url(r'^getAlergiPasien', views.getAlergiPasien, name='emrrj_getAlergiPasien'),

        url(r'^login/',include([
                url(r'^$', views_dashboard.login, name='emrj_login'),
                url(r'^getCabang', views_dashboard.getCabang, name='emrrj_login_getCabang'),
                url(r'^getUser', views_dashboard.getUser, name='emrrj_login_getUser'),
            ])   
        ),
       
        url(r'^cppt/',include([
                url(r'^$', views.page_cppt, name='emrj_page_cppt'),
                url(r'^getMRICD9', views.getMRICD9, name='emrrj_getMRICD9'),
                url(r'^getDignosaKerjaCPPT', views.getDignosaKerjaCPPT, name='emrrj_getDignosaKerjaCPPT'),
                url(r'^save', views.save_cppt, name='emrrj_save_cppt'),
                url(r'^getDataCPPT', views.getDetailCPPT, name='emrrj_getDetailCPPT'),
                url(r'^getHPL', views.getHPL, name='emrrj_getHPL'),
                url(r'^list', views.getCPPTPasien, name='emrrj_getCPPTPasien'),

            ])   
        ),
        
        url(r'^upload/',include([
                url(r'^$', views.upload_image, name='emrj_upload_image_cppt'),
                url(r'^crm-lama', views.getPDFCRM, name='getPDFCRM'),
                # url(r'^getCabang', views_dashboard.getCabang, name='emrrj_login_getCabang'),
                # url(r'^getUser', views_dashboard.getUser, name='emrrj_login_getUser'),
                # url(r'^save', operasi.savelaporanTindakanBedah_prosedurInvasif, name='emri_savelaporanTindakanBedah_prosedurInvasif'),
                # url(r'^upload', operasi.upload_laporanTindakanBedah_prosedurInvasif, name='emri_upload_laporanTindakanBedah_prosedurInvasif'),
                # url(r'^print', operasi.printlaporanTindakanBedah_prosedurInvasif, name='emri_printlaporanTindakanBedah_prosedurInvasif'),
            ])   
        ),
        
        url(r'^eresep/',include([
                url(r'^$', views.eResepPage, name='emrrj_eResepPage'),
                url(r'^crud', views.crudResepRJ, name='emrrj_crudResepRJ'),
                url(r'^pickerHistoryResepManual', views.pickerHistoryResepManual, name='emrrj_pickerHistoryResepManual'),
                url(r'^print-entry-resep', views.printResep, name='emrrj_printResep'),
                url(r'^delete', views.deleteEresep, name='emrrj_deleteEresep'),
            ])   
        ),
       
        url(r'^racikan-resep/',include([
                url(r'^$', views.eResepRacikPage, name='emrrj_eResepRacikPage'),
                url(r'^crud', views.crudRacikanResep, name='emrrj_crudRacikanResep'),
                # url(r'^pickerHistoryResepManual', views.pickerHistoryResepManual, name='emrrj_pickerHistoryResepManual'),
            ])   
        ),
        
        url(r'^e-lab/',include([
                url(r'^$', views.page_elab, name='emrrj_page_elab'),
                url(r'^save', views.save_elabrad, name='emr_save_elabrad'),
                url(r'^del', views.delElabRad, name='emrrj_delElabRad'),
                
            ])   
        ),
        
        url(r'^e-rad/',include([
                url(r'^$', views.page_erad, name='emrrj_page_erad'),
                url(r'^save', views.save_elabrad, name='emr_save_elabrad'),
                url(r'^del', views.delElabRad, name='emrrj_delElabRad'),
                
            ])   
        ),
        
        url(r'^e-panggil/',include([
                url(r'^$', views.panggilDisplayNode, name='emrrj_panggilDisplay'),
                # url(r'^save', views.save_elabrad, name='emr_save_elabrad'),
                # url(r'^del', views.delElabRad, name='emrrj_delElabRad'),
                
            ])   
        ),
        
        url(r'^riwayat-cppt/',include([
                url(r'^$', views.getRiwayatPemeriksaanByNORM, name='emrrj_getRiwayatPemeriksaanByNORM'),
                url(r'^detail', views.getRiwayatPemeriksaanByNORMDetail, name='emr_getRiwayatPemeriksaanByNORMDetail'),
                # url(r'^del', views.delElabRad, name='emrrj_delElabRad'),
                
            ])   
        ),

        
        #klinik pcare briging
        url(r'^bridgingPostRujukanSpesialis',views_pcare.bridgingPostRujukanSpesialis, name='bridgingPostRujukanSpesialis'),
        url(r'^pickerpcare',views_pcare.getDataPickerPCAREBPJS, name='getDataPickerPCAREBPJS'),
        url(r'^getDataRujukanBridging',views_pcare.getkunjunganRujukanBridging, name='getkunjunganRujukanBridging'),
        url(r'^crudBridgingBPJSLab',views_pcare.crudBridgingBPJSLab, name='crudBridgingBPJSLab'),
        url(r'^delHasilLabBridgingBPJSLab',views_pcare.delHasilLabBridgingBPJSLab, name='delHasilLabBridgingBPJSLab'),
        url(r'^printSuratRujukanPCAREBPJS',views_pcare.printSuratRujukanPCAREBPJS, name='printSuratRujukanPCAREBPJS'),
        url(r'^printSuratKunjunganPCAREBPJS',views_pcare.printSuratKunjunganPCAREBPJS, name='printSuratKunjunganPCAREBPJS'),
        url(r'^printSuratSPPPCAREBPJS',views_pcare.printSuratSPPPCAREBPJS, name='printSuratSPPPCAREBPJS'),
        url(r'^getBridgingBPJSObat',views_pcare.getBridgingBPJSObat, name='getBridgingBPJSObat'),
        url(r'^delBridgingBPJSObat',views_pcare.delBridgingBPJSObat, name='delBridgingBPJSObat'),
        url(r'^cekDiagnosaTACCS',views_pcare.cekDiagnosaTACCS, name='cekDiagnosaTACCS'),

        #ICD10
        url(r'^icdtens/',include([
            # url(r'^$', views.getHistoryEresepRanap, name='emrrj_getHistoryEresepRanap'),
            url(r'^findStatusKasus', views.findStatusKasus, name='emrrj_icd10_findStatusKasus'),
            url(r'^findStatusDiagnosaKlaim', views.findStatusDiagnosaKlaim, name='emrrj_icd10_findStatusDiagnosaKlaim'),
            url(r'^findStatusDiagnosaKlaimAwal', views.findStatusDiagnosaKlaimAwal, name='emrrj_icd10_findStatusDiagnosaKlaimAwal'),
            url(r'^getDignosaKerjaCPPT', views.getDignosaKerjaCPPT, name='emrrj_icd10_getDignosaKerjaCPPT'),
            url(r'^getDiagnosaPenyakit', views.getDiagnosaPenyakit, name='emrrj_icd10_getDiagnosaPenyakit'),

        ])
        ),
    ])   
    ),
]