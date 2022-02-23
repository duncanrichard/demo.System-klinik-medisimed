from django.conf.urls import url, include
from . import views
from . import shift
from . import privelige
from . import data_pasien

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),

    url(r'^shift/', include([
        url(r'^setShift', shift.setShift),
        url(r'^tutupShift', shift.tutupShift),
        url(r'^edit', shift.editShift),
        url(r'^updateShift', shift.updateShift),
        url(r'^getShiftList', shift.getShiftList),
        url(r'^getShift', shift.getShift),
    ])),

    url(r'^privilege/', include([
        url(r'^$', privelige.dashboard, name='privilege'),
        url(r'^menu/',privelige.menu, name='menu'),
        url(r'^menu_priv/',privelige.menu_priv, name='menu_priv'),
        url(r'^menu_post',privelige.menu_post, name='menu_post'),
        url(r'^user/',privelige.user, name='user'),

        url(r'^navbars/',privelige.navbars, name='navbars'),
        url(r'^navbars_priv/',privelige.navbars_priv, name='navbars_priv'),
        url(r'^navbars_post',privelige.navbars_post, name='navbars_post'),
        url(r'^subnavbars_priv/',privelige.subnavbars_priv, name='subnavbars_priv'),
        url(r'^subnavbars_post',privelige.subnavbars_post, name='subnavbars_post'),

        url(r'^menubars/',privelige.menubars, name='menubars'),
        url(r'^menubars_priv/',privelige.menubars_priv, name='menubars_priv'),
        url(r'^submenubars_priv/',privelige.submenubars_priv, name='submenubars_priv'),
        url(r'^menubars_post',privelige.menubars_post, name='menubars_post'),
        url(r'^submenubars_post',privelige.submenubars_post, name='submenubars_post'),


        ])
    ),
    url(r'^data_pasien/', include ([
        url(r'^$',data_pasien.data_pasien, name='data_pasien'),
        url(r'^getKelamin', data_pasien.getKelamin),
        url(r'^getDataKelamin', data_pasien.getDataKelamin),
        url(r'^getProvinsi', data_pasien.getProvinsi),
        url(r'^getDataProvinsi', data_pasien.getDataProvinsi),
        url(r'^getKabupaten', data_pasien.getKabupaten),
        url(r'^getDataKabupaten', data_pasien.getDataKabupaten),
        url(r'^getKecamatan', data_pasien.getKecamatan),
        url(r'^getDataKecamatan', data_pasien.getDataKecamatan),
        url(r'^getKelurahan', data_pasien.getKelurahan),
        url(r'^getDataKelurahan', data_pasien.getDataKelurahan),
        url(r'^getKlpPasien', data_pasien.getKlpPasien),
        url(r'^getDataKlpPasien', data_pasien.getDataKlpPasien),
        url(r'^getCustomer', data_pasien.getCustomer),
        url(r'^getDataCustomer', data_pasien.getDataCustomer),
        url(r'^getPasien', data_pasien.getPasien),
        url(r'^getDataPasien', data_pasien.getDataPasien),
    ])),


]
