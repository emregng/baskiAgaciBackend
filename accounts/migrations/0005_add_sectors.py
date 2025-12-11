from django.db import migrations

def add_sectors(apps, schema_editor):
    Sector = apps.get_model('accounts', 'Sector')
    sector_names = [
        "Ofis Kırtasiye", "Kağıtçı", "Malzeme – Boya", "Promosyon Ürünleri", "Bez Çantacı",
        "Oto Kokucusu", "Magnetçi", "Islak Mendil", "Karton Bardakçı", "Ambalajcı",
        "Bayrakçı", "Yaka Kartı", "Davetiyeciler", "Plastik Poşet", "Anlaşmalı Matbaa",
        "Neon Tabelacı", "Menücü", "Damla Etiket", "Bobin Etiket", "Ürün Fotoğrafçısı",
        "Tekstil Baskı", "Anahtarlık Üretici", "Araç Giydirme", "Yayın evi", "Reklam – Vinil",
        "Plaketçi", "Dijital Baskı", "Tabelacılar", "Ajanslar – Matbaa", "Saatçiler",
        "Grafiker", "Sosyal Medyacı", "CEO", "Web Tasarımcı", "Çakmak", "Serigrafçı",
        "Kolici", "Pleksici", "Anahtarlıkçı", "Ör Kart", "Nikah Şekercisi",
        "Organizasyon Firması", "Düğün Fotoğrafçısı"
    ]
    for i, name in enumerate(sector_names):
        Sector.objects.get_or_create(name=name, defaults={'is_active': True, 'order': i})

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_sector'),
    ]

    operations = [
        migrations.RunPython(add_sectors),
    ]