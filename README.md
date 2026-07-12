# Toplu Kişiselleştirilmiş Mail Gönderme Aracı

Flask + SMTP kullanarak, CSV listesindeki her alıcıya kendine özel
değerlerle (`{isim}`, `{x}`, `{y}`, `{z}` gibi) doldurulmuş mail gönderen
küçük bir web uygulaması.

## Dosyalar

- `app.py` — Flask uygulaması ve gönderim mantığı
- `templates/index.html` — dosya yükleme formu
- `templates/preview.html` — gönderim öncesi önizleme
- `templates/result.html` — gönderim sonucu raporu
- `ornek_aliciler.csv` — örnek alıcı listesi
- `ornek_sablon.html` — örnek mail şablonu
- `.env.example` — ortam değişkeni örneği

## Kurulum

```bash
cd mailapp
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env dosyasını açıp SMTP bilgilerinizi girin
```

### Gmail kullanıyorsanız

Normal şifreniz çalışmaz. Google hesabınızda "2 Adımlı Doğrulama"yı açıp
**Uygulama Şifresi (App Password)** oluşturmanız ve `SMTP_PASS` olarak onu
girmeniz gerekir: https://myaccount.google.com/apppasswords

## Çalıştırma

```bash
python app.py
```

Tarayıcıda `http://127.0.0.1:5000` adresine gidin.

## Kullanım Akışı

1. Ana sayfada CSV alıcı listenizi yükleyin (sütunlar: `email,isim,x,y,z,...`)
2. Mail konusunu yazın — placeholder kullanabilirsiniz: `Merhaba {isim}`
3. HTML veya TXT mail şablonu dosyanızı yükleyin
4. "Önizle" butonuna basın, ilk alıcı için nasıl göründüğünü kontrol edin
5. Onaylayıp gönderin. Sonuç sayfasında her alıcı için başarılı/başarısız
   durumu görürsünüz.

## CSV Formatı

```csv
email,isim,x,y,z
ahmet@ornek.com,Ahmet,1,2,3
ayse@ornek.com,Ayşe,4,5,6
```

- `email` sütunu zorunludur.
- Diğer sütunlar (`isim`, `x`, `y`, `z`, ... istediğiniz kadar) şablonda
  `{sutun_adi}` şeklinde kullanılabilir.

## Önemli Notlar

- **Sadece izinli (opt-in) alıcılara** mail gönderin. İzinsiz toplu mail
  göndermek KVKK/GDPR/CAN-SPAM gibi kanunlara aykırıdır ve SMTP
  sağlayıcınızın hesabınızı kapatmasına yol açabilir.
- Mailinize her zaman bir **"abonelikten çık" linki** ekleyin.
- `SEND_DELAY_SECONDS` ile gönderimler arasına bekleme koyulmuştur; bu,
  sağlayıcının spam koruma sistemlerine takılma riskini azaltır.
- Büyük listelerde (binlerce alıcı) SMTP yerine SendGrid, Amazon SES,
  Mailgun gibi toplu mail servislerinin kullanılması önerilir.
