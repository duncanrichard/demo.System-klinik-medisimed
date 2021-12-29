$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();

    $('.modal').on('hidden.bs.modal', function(e) {
        $('body').removeAttr("style");
    })
});

function menuEnable(id) {
    $('#' + id).removeClass('disabled');
}

function menuDisable(id) {
    $('#' + id).addClass('disabled');
}

function btnEnable(id) {
    $('#' + id).attr("disabled", false);
}

function btnDisable(id) {
    $('#' + id).attr("disabled", true);
}

function setEnable(id) {
    btnEnable(id)
}

function setDisable(id) {
    btnDisable(id)
}

function setCheck(id) {
    $('#' + id).prop('checked', true);
}

function setUnCheck(id) {
    $('#' + id).prop('checked', false);
}

function setReadOnly(id) {
    $('#' + id).prop('readonly', true);
}

function setUnReadOnly(id) {
    $('#' + id).prop('readonly', false);
}

function setEmpty(id) {
    $('#' + id).val('');
}

function isEmpty(str) {
    return (!str || 0 === str.length);
}

function isBlank(str) {
    return (!str || /^\s*$/.test(str));
}

function checkNULL(str) {
    return str == null ? '' : str.trim();
}

function format_tanggal(date) {
    if (date != null) {
        bulanIndo = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober',
            'November', 'Desember'
        ];

        tanggal = date.split("-")[2];
        bulan = date.split("-")[1];
        tahun = date.split("-")[0];

        return tanggal + " " + bulanIndo[Math.abs(bulan)] + " " + tahun;
    }

    return '';
}

function convertToRupiah(angka, separator = null) {
    let is_negative = false;

    if(angka < 0){
        is_negative = true
        angka = angka * -1;
    }

    var rupiah = '';
    var angkarev = angka.toString().split('').reverse().join('');
    for (var i = 0; i < angkarev.length; i++) {
        if (i % 3 == 0) {
            if (separator == null) {
                rupiah += angkarev.substr(i, 3) + ',';
            } else {
                rupiah += angkarev.substr(i, 3) + '.';
            }
        }
    }

    if(is_negative == false){
        return rupiah.split('', rupiah.length - 1).reverse().join('');
    } else {
        return '-' + rupiah.split('', rupiah.length - 1).reverse().join('');
    }
}

function convertToAngka(rupiah) {
    if(rupiah != undefined){
        let is_negative = false;

        if(rupiah.charAt(0) == '-'){
            is_negative = true
            rupiah = rupiah.substring(1);
        }

        if(is_negative == false){
            return checkIsNaN(parseInt(rupiah.replace(/,/g, '').replace(/,.*|[^0-9]/g, ''), 10));
        } else {
            return checkIsNaN(parseInt(rupiah.replace(/,/g, '').replace(/,.*|[^0-9]/g, ''), 10)) * -1;
        }
    } else {
        return 0;
    }
}

function inputRupiah(e, func = null) {
    if (e != null) {
        e.addEventListener('keyup', function(f) {
            var rp = formatRupiah(e.value);
            e.value = rp
        });

        if (func != null) {
            func()
        }
    }
}

function formatRupiah(angka, prefix) {
    var number_string = angka.toString().replace(/[^,\d]/g, '').toString(),
        split = number_string.split(','),
        sisa = split[0].length % 3,
        rupiah = split[0].substr(0, sisa),
        ribuan = split[0].substr(sisa).match(/\d{1,3}/gi);

    if (ribuan) {
        separator = sisa ? '.' : '';
        rupiah += separator + ribuan.join('.');
    }

    rupiah = split[1] != undefined ? rupiah + ',' + split[1] : rupiah;
    return prefix == undefined ? rupiah : (rupiah ? 'Rp. ' + rupiah : '');
}

function checkIsNaN(value) {
    return isNaN(value) == true ? 0 : value;
}

function showBatch(data) {  
    data.forEach(e => {
        $("#" + e).show();
    });
}

function hideBatch(data) {  
    data.forEach(e => {
        $("#" + e).hide();
    });
}