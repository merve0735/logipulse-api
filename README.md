# LogiPulse API

Lojistik/kargo/kurye şirketleri için backend API — rota, araç, kurye ve teslimat takibi.

## Notlar

**Konum girişi (tracking):** Demo paneldeki "Konumumu Güncelle" alanı şimdilik manuel enlem/boylam girişiyle çalışır. Gerçek bir mobil kurye uygulamasında bu bilgi telefonun GPS'inden otomatik olarak alınıp gönderilir; burada sadece MVP seviyesinde konsepti göstermek için manuel giriş kullanılıyor.

**KVKK / Kişisel Veri Notu:** Gerçek kullanımda driver konum verisi kişisel veri sayılabilir. Bu yüzden kullanıcı bilgilendirmesi, açık rıza, veri saklama süresi ve erişim yetkileri ayrıca tasarlanmalıdır.

## Testleri Çalıştırma

Testler `logipulse_test` adında ayrı bir veritabanı kullanır; gerçek `logipulse` verisine dokunmaz.

**Lokal (Docker üzerinden):**

```bash
docker compose exec api pytest -q
```

**GitHub Actions:** `main` dahil her branch'e `push` veya `pull request` açıldığında `.github/workflows/tests.yml` otomatik çalışır. Adımlar: Python 3.11 kurulumu → bağımlılıkların yüklenmesi → geçici bir MongoDB servisi ayağa kaldırılması → `pytest -q` çalıştırılması. Sonucu GitHub üzerindeki PR/commit sayfasındaki "Checks" (Actions) sekmesinden görebilirsin.
