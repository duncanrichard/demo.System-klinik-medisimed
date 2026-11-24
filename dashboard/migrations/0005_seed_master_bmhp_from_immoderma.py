from django.db import migrations


BMHP_NAMES = [
    "Flawless Facial Wash",
    "Flawless Cleanser",
    "Massage krim",
    "Facial Scrub",
    "Soft Smooth Comedo",
    "Tisu Facial",
    "IMMODERMA Bright & Glow Collagen Mask~",
    "Handscoon",
    "IMMODERMA Brighthening C Collagen Mask",
    "Acne Flawless Facial Wash",
    "IMMODERMA Aloe Vera Shooting Mask",
    "IMMODERMA Dead Sea Mud Mask",
    "Air Mawar",
    "IMMODERMA Genuine Pearl Rubber Mask",
    "IMMODERMA Golden Powder Rubber Mask",
    "IMMODERMA Milk Collagen Paper Gel Mask",
    "IMMODERMA Tea Tree Rubber Mask",
    "Masker Peel Off Coklat",
    "White & Glow Serum Immo",
    "Spuit 1 CC (Isi 100 Pcs)",
    "Spuit 5 CC (Isi 100 Pcs)",
    "Cairan AHA/cairan Hydrapeel",
    "Masker Original 30 gr",
    "Masker Peel Off Strawberry",
    "Spuit 3 CC (Isi 100 Pcs)",
    "Whitening Kojic Ampul",
    "Nacl 100 CC",
    "Gel IPL",
    "Nurse Cap",
    "Jarum Derma 12",
    "Anastesi Cream Kecil",
    "Penta White",
    "Giga White Peel",
    "Bleaching",
    "IV Abbocath No. 24 GEA",
    "Infuset GEA",
    "Alkohol Swab",
    "Plesterin Bulat",
    "Ultrafix 5X5",
    "Provevit inj",
    "Prove C inj / Lavit C",
    "Neurobion Inj",
    "Carbon Cream",
    "Meso Needle 32G",
    "RF Cream",
    "Face Nade",
    "Tabung PRP/EDTA",
    "Wove Hair Scalp",
    "EMINOX 5%",
    "Hair loss",
    "Detox Cream",
    "Botox 100 unit",
    "Nacl 25 CC",
    "Penta Acne",
    "Masker Tablet",
    "Cutegel (HA) / Staris SkinBooster",
    "Trilac inj 10 mg per 5 ml",
    "Cefotaxime",
    "Needle 30G Kuning",
    "Pluryal Plump",
    "Currunex",
    "Redness - Id",
    "Akn id",
    "Dexametasone inj",
    "Shooting cream/restructurer",
    "Pluryal Shine",
    "Whitening Solution",
    "Glutanex Glow Skinbooster",
    "Silk PDNA",
    "Kondom Jari",
    "Serum Glowing",
    "DNA-Peptide",
    "Needle 30G BD Coklat",
    "Penta White Cell Dna",
    "Steamcell / Secretom",
    "Pink booster vial / Pink Aging",
    "TIGF",
    "NCTF",
    "Filler Cara Soft",
    "Oxygeneo / Neobright",
    "Wing Needle",
    "Slimming Care",
    "Lidocain inj",
    "Furosemid inj",
    "Membran Fat Freeze",
    "Nacl 500 CC",
    "Speculum Vagina",
    "Cateter",
    "Underpad Hijau",
    "Aquadest",
    "V-line lippolab",
]


def replace_master_bmhp(apps, schema_editor):
    BMHP = apps.get_model("dashboard", "BMHP")
    TreatmentBMHP = apps.get_model("dashboard", "TreatmentBMHP")

    # A BMHP can be referenced by a treatment, so clear dependent mappings first.
    TreatmentBMHP.objects.all().delete()
    BMHP.objects.all().delete()

    names = []
    seen = set()
    for name in BMHP_NAMES:
        normalized_name = " ".join(name.split())
        key = normalized_name.casefold()
        if normalized_name and key not in seen:
            names.append(normalized_name)
            seen.add(key)

    BMHP.objects.bulk_create([BMHP(nama_bmhp=name) for name in names])


class Migration(migrations.Migration):
    dependencies = [("dashboard", "0004_apoteker_preparation")]

    operations = [
        migrations.RunPython(replace_master_bmhp, migrations.RunPython.noop),
    ]
