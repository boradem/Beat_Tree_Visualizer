# Beat Tree Visualizer 🎵🌳

Şarkı beat'lerini gerçek zamanlı olarak ağaç yapısı şeklinde görselleştiren Python uygulaması.

## Özellikler

- 🎶 Audio dosyalarından otomatik beat detection
- 🌳 Beat'lere göre dinamik ağaç yapısı görselleştirme
- 🎨 Beat yoğunluğuna göre renk ve boyut değişimi
- ⏯️ Oynat/Duraklat kontrolü
- 📊 Gerçek zamanlı beat takibi

## Kurulum

1. FFmpeg yükleyin (audio formatları için gerekli):
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` veya `sudo yum install ffmpeg`
   - Windows: [FFmpeg resmi sitesinden](https://ffmpeg.org/download.html) indirin

2. Gerekli Python paketlerini yükleyin:

```bash
pip install -r requirements.txt
```

**Not**: spotdl için ek kurulum gerekebilir. Detaylar için: https://spotdl.readthedocs.io/

## Kullanım

### Dosya yolu ile:
```bash
python beat_tree_visualizer.py <şarkı_dosyası>
```

### YouTube linki ile:
```bash
python beat_tree_visualizer.py https://www.youtube.com/watch?v=VIDEO_ID
# veya
python beat_tree_visualizer.py https://youtu.be/VIDEO_ID
```

### Spotify linki ile:
```bash
python beat_tree_visualizer.py https://open.spotify.com/track/TRACK_ID
```

### Örnekler

```bash
# Dosya yolu
python beat_tree_visualizer.py my_song.mp3

# YouTube
python beat_tree_visualizer.py https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Spotify
python beat_tree_visualizer.py https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC
```

### Desteklenen Formatlar ve Kaynaklar

**Dosya formatları:**
- MP3, WAV, FLAC, M4A
- Ve diğer librosa'nın desteklediği formatlar

**Online kaynaklar:**
- YouTube (yt-dlp ile)
- Spotify (spotdl ile)

## Kontroller

- **SPACE**: Oynat/Duraklat
- **R**: Yeniden başlat
- **ESC**: Çıkış

## Nasıl Çalışır?

1. Uygulama şarkıyı yükler ve beat'leri otomatik olarak tespit eder
2. Her beat'te ağaç yapısı oluşturulur
3. Beat yoğunluğu (enerji seviyesi) ağacın:
   - Renklerini
   - Dal uzunluklarını
   - Açı farklarını
   - Yaprak boyutlarını
   
   etkiler

4. Ağaç yapısı her beat'te güncellenir ve görsel olarak gerçek zamanlı beat'leri gösterir

## Teknik Detaylar

- **Beat Detection**: librosa kütüphanesi kullanılarak yapılmaktadır
- **Görselleştirme**: Pygame ile gerçek zamanlı render
- **Audio Oynatma**: Pygame mixer ile senkron oynatma
- **Ağaç Algoritması**: Recursive fractal ağaç yapısı
- **YouTube İndirme**: yt-dlp kütüphanesi
- **Spotify İndirme**: spotdl komut satırı aracı

## Gereksinimler

**Sistem Gereksinimleri:**
- Python 3.8+
- FFmpeg (audio formatları için gerekli)

**Python Paketleri:**
- librosa
- pygame
- numpy
- matplotlib
- soundfile
- yt-dlp (YouTube için)
- spotdl (Spotify için)

## Notlar

- YouTube linkleri için yt-dlp otomatik olarak çalışır
- Spotify linkleri için spotdl'nin yüklü olması ve PATH'de bulunması gerekir
- İndirilen dosyalar geçici dizinde saklanır ve görselleştirme sonrası silinebilir

