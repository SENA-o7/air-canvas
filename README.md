# Air Canvas - Computer Vision & Hand Tracking

Bu proje, Python, OpenCV ve MediaPipe kullanılarak geliştirilmiş bir bilgisayarlı görü (Computer Vision) ve el takibi (Hand Tracking) uygulamasıdır. Kamera üzerinden el ve parmak hareketlerini algılayarak ekranda gerçek zamanlı çizim yapabilme, etkileşimli şekiller (Ramadan Painter vb.) oluşturma gibi yapay zeka destekli özellikler içerir.

## 🚀 Başlangıç için Neler Öğrendik? (Kazanımlarımız)

Projeyi geliştirirken sadece kod yazmayı değil, sıfırdan bir projenin profesyonel altyapısını kurmayı da öğrendik:

- **Profesyonel Geliştirme Ortamı Kurulumu:** Python projeleri için **virtual environment (venv)** kurarak, her projenin bağımsız bir çalışma alanına sahip olması gerektiğini deneyimledik. IDE (PyCharm) üzerinden interpreter yönetimini ve izole ortam oluşturmayı öğrendik.
- **Bağımlılık (Dependency) ve Hata Yönetimi:** Kurulum sürecinde karşılaşılan MediaPipe import hatalarını analiz edip pip ile paket yönetimi yaparak debugging (hata ayıklama) pratiği kazandık.
- **Gerçek Zamanlı Görüntü İşleme (Computer Vision):** OpenCV ve MediaPipe kullanarak kameradan canlı veri almayı ve bu veriyi kare kare işlemeyi öğrendik.
- **El Haritalama (Hand Tracking):** Elin 21 farklı landmark noktasını (eklem yerleri) tespit edip, bu noktaların koordinatlarını kullanarak el hareketleriyle tetiklenen fonksiyonlar geliştirdik.
- **Algoritma ve Mantık Kurma:** Parmakların açık/kapalı durumlarını matematiksel hesaplamalar ve algoritmalarla tespit edip; silgi modu, çizim yapma, serçe parmağıyla hilal veya yıldız yağmuru gibi interaktif modlar programladık.

## 📁 Proje İçeriği

- `ramadan_painter_v2.py`: Ramazan temalı, ultra neon altın efektli etkileşimli çizim uygulaması.
- `dersler/01_el_landmarks.py`: Ellerdeki 21 noktanın gökkuşağı renkleriyle algılanması.
- `dersler/02_parmak_sayma.py` & `03_mesafe_olcer.py` vb.: Parmak sayımı, mesafe tahmini gibi temel computer vision pratikleri.

---
👤 **Geliştirici:** [SENA-o7](https://github.com/SENA-o7)
