from django import forms

from .models import BMHP, TreatmentBMHP


class BMHPForm(forms.ModelForm):
    class Meta:
        model = BMHP
        fields = ["nama_bmhp"]
        widgets = {
            "nama_bmhp": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Contoh: Kapas alkohol",
                    "autocomplete": "off",
                }
            )
        }


class TreatmentBMHPForm(forms.ModelForm):
    class Meta:
        model = TreatmentBMHP
        fields = ["bmhp", "jumlah", "satuan"]
        widgets = {
            "bmhp": forms.Select(attrs={"class": "form-control"}),
            "jumlah": forms.NumberInput(
                attrs={"class": "form-control", "min": "0.01", "step": "0.01"}
            ),
            "satuan": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Contoh: CC atau pcs", "maxlength": 30}
            ),
        }

    def clean_jumlah(self):
        jumlah = self.cleaned_data["jumlah"]
        if jumlah <= 0:
            raise forms.ValidationError("Jumlah harus lebih besar dari 0.")
        if jumlah.as_tuple().exponent < -2:
            raise forms.ValidationError("Jumlah maksimal dua angka di belakang koma.")
        return jumlah
