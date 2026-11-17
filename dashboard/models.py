from django.db import models


class BMHP(models.Model):
    nama_bmhp = models.CharField("Nama BMHP", max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "BMHP"
        ordering = ["nama_bmhp"]

    def __str__(self):
        return self.nama_bmhp


class TreatmentBMHP(models.Model):
    treatment_id = models.CharField("ID Treatment", max_length=50)
    bmhp = models.ForeignKey(BMHP, on_delete=models.PROTECT, related_name="treatment_usages")
    jumlah = models.DecimalField("Jumlah", max_digits=12, decimal_places=3)
    satuan = models.CharField("Satuan", max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "TREATMENT_BMHP"
        ordering = ["treatment_id", "bmhp__nama_bmhp"]
        unique_together = [("treatment_id", "bmhp", "satuan")]


class ApotekerPreparation(models.Model):
    transaction_id = models.CharField("Nomor Transaksi", max_length=50)
    transaction_detail_number = models.IntegerField("Nomor Detail Transaksi")
    prepared_at = models.DateTimeField("Waktu Disiapkan", auto_now_add=True)
    prepared_by = models.CharField("Disiapkan Oleh", max_length=100, blank=True)

    class Meta:
        db_table = "APOTEKER_PERSIAPAN_BMHP"
        unique_together = [("transaction_id", "transaction_detail_number")]
