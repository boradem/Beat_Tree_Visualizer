# Beat Tree Visualizer

Müzik, sadece duyduğumuz bir şey değil; hissettiğimiz ve bazen de görmek istediğimiz bir deneyimdir. Beat Tree Visualizer, en sevdiğiniz şarkıların ritmini ve enerjisini alıp, müziğin nabzıyla büyüyen ve nefes alan dinamik bir ağaca dönüştürür.

Bu proje, ses dosyalarını analiz ederek ritim vuruşlarını (beat) yakalar ve bu veriyi gerçek zamanlı bir görsel şölene çevirir. Şarkının yoğunluğuna göre renk değiştiren yapraklar ve ritme ayak uyduran dallar ile müziğinizi izlemenin keyfini çıkarın.

## Öne Çıkan Özellikler

- **Akıllı Ritim Analizi**: Yüklediğiniz ses dosyasının ritmini ve vuruş noktalarını otomatik olarak algılar.
- **Canlı Görselleştirme**: Müziğin her vuruşunda ağacın nasıl tepki verdiğini anlık olarak izleyin.
- **Dinamik Atmosfer**: Şarkının enerjisine göre değişen renk paletleri ve büyüme efektleri.
- **Kolay Kontrol**: Oynatma, duraklatma ve ses kontrolü parmaklarınızın ucunda.

## Kurulum ve Başlangıç

Bu görsel deneyimi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları takip edebilirsiniz.

1. **Gerekli Araçlar**: Ses formatlarını işleyebilmek için FFmpeg kütüphanesine ihtiyacınız olacak.
   - macOS kullanıcıları: `brew install ffmpeg`
   - Windows ve Linux kullanıcıları için detaylı bilgi: [FFmpeg İndir](https://ffmpeg.org/download.html)

2. **Paketlerin Yüklenmesi**: Proje dizininde terminali açın ve gerekli Python kütüphanelerini yükleyin:

```bash
pip install -r requirements.txt
```

*Not: Spotify entegrasyonu için ek kurulum gerekebilir.*

## Nasıl Kullanılır?

Uygulamayı çalıştırmak oldukça basittir. İster bilgisayarınızdaki bir dosyayı, ister YouTube veya Spotify bağlantısını kullanabilirsiniz.

### Yerel Dosya ile Başlatma
```bash
python beat_tree_visualizer.py sarki_dosyasi.mp3
```

### YouTube Bağlantısı ile Başlatma
Sevdiğiniz bir YouTube videosunun linkini yapıştırmanız yeterli:
```bash
python beat_tree_visualizer.py https://www.youtube.com/watch?v=VIDEO_ID
```

### Spotify Bağlantısı ile Başlatma
```bash
python beat_tree_visualizer.py https://open.spotify.com/track/TRACK_ID
```

## Kontroller

Uygulama çalışırken klavyenizle şu komutları verebilirsiniz:

- **BOŞLUK**: Oynat / Duraklat
- **YÖN TUŞLARI**: İleri/Geri sarma ve Ses kontrolü
- **R**: Görselleştirmeyi sıfırla
- **T**: Temayı değiştir
- **D**: Otomatik tema değişimini aç/kapat
- **ESC**: Çıkış

## Teknolojinin Arkasındaki Büyü

Bu projenin kalbinde birkaç güçlü kütüphane yatıyor:
- **Librosa**: Müziğin matematiğini çözer ve ritmi algılar.
- **Pygame**: Hesaplanan verileri akıcı bir görsel deneyime dönüştürür.
- **Fractal Algoritmalar**: Doğadaki ağaç yapısını taklit ederek her seferinde benzersiz bir görüntü oluşturur.

Umarım bu görselleştirici, müzik dinleme deneyiminize yeni bir boyut katar. Keyifli seyirler!

