var klik_kounter = 0;
var global_KodeTransferApt = 'ADL002'
var global_NamaTransferApt = 'BIAYA OBAT DAN ALKES'

function getTodayDateTime() {
    var today = new Date();
    var date = today.getFullYear() + '-' + (today.getMonth() + 1).toString().padStart(2, "0") + '-' + today.getDate().toString().padStart(2, "0");
    var time = today.getHours().toString().padStart(2, "0") + ":" + today.getMinutes().toString().padStart(2, "0") + ":" + today.getSeconds().toString().padStart(2, "0");
    var dateTime = date + ' ' + time;

    return {
        'date': date,
        'time': time,
        'datetime': dateTime
    };
}

function exitBack(e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    window.history.back();
}

function checkUmur(umr = null) {
    var startingDate;
    if (typeof umr == "string") {
        startingDate = umr;
    } else {
        startingDate = $('#tgl_lahir').val();
    }

    var startDate = new Date(new Date(startingDate).toISOString().substr(0, 10));

    var endingDate = new Date().toISOString().substr(0, 10); // need date in YYYY-MM-DD format

    var endDate = new Date(endingDate);
    if (startDate > endDate) {
        var swap = startDate;
        startDate = endDate;
        endDate = swap;
    }
    var startYear = startDate.getFullYear();
    var february = (startYear % 4 === 0 && startYear % 100 !== 0) || startYear % 400 === 0 ? 29 : 28;
    var daysInMonth = [31, february, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    var yearDiff = endDate.getFullYear() - startYear;
    var monthDiff = endDate.getMonth() - startDate.getMonth();
    if (monthDiff < 0) {
        yearDiff--;
        monthDiff += 12;
    }
    var dayDiff = endDate.getDate() - startDate.getDate();
    if (dayDiff < 0) {
        if (monthDiff > 0) {
            monthDiff--;
        } else {
            yearDiff--;
            monthDiff = 11;
        }
        dayDiff += daysInMonth[startDate.getMonth()];
    }

    $('#usia_thn').val(yearDiff);
    $('#usia_bln').val(monthDiff);
    $('#usia_hari').val(dayDiff);
    return {
        tahun: yearDiff,
        bulan: monthDiff,
        hari: dayDiff,
    };
}

function calculateAge(birthday) { // birthday is a date
    var ageDifMs = Date.now() - birthday.getTime();

    if (ageDifMs > 24 * 60 * 60 * 1000 * 1) {
        ageDifMs = ageDifMs - 20 * 60 * 60 * 1000 * 1
    } else {
        ageDifMs = ageDifMs - (ageDifMs - 3600000);
    }

    var ageDate = new Date(ageDifMs); // miliseconds from epoch
    return {
        tahun: Math.abs(ageDate.getUTCFullYear() - 1970),
        bulan: Math.abs(ageDate.getMonth()),
        tanggal: Math.abs(ageDate.getDate()),
    };
}

function enterFocusTo(id, nextId, callback = null) {
    $('#' + id).keypress(function (event) {
        event.stopImmediatePropagation();
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if (keycode == '13' || keycode == '9') {
            $('#' + nextId).focus();

            if (callback != null) {
                callback()
            }
            event.preventDefault();
        }

    })
}

function exitBack(e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    window.history.back();
}