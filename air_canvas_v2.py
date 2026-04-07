import cv2
import mediapipe as mp
import numpy as np
import colorsys

"""
🎨 PROFESYONEL AIR CANVAS V2: HASSAS SÜRÜM
-------------------------------------------------
Bu versiyon, kullanıcının geri bildirimlerine göre optimize edilmiştir.
Hatalar Giderildi:
1. Kesik Çizim Problemi: Sürekli çizgi çizme ve mesafe kontrolü iyileştirildi.
2. Silgi-Kalem Geçişi: Modlar arasındaki çakışmalar ve takılmalar çözüldü.
3. Sessiz Duraklatma: 5 parmak modundaki geçişler hızlandırıldı.
-------------------------------------------------
"""

# 1. KURULUM VE MEDIAPIPE AYARLARI
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1, 
    min_detection_confidence=0.7, # Hassasiyeti biraz düşürerek takipleri kolaylaştırdık
    min_tracking_confidence=0.7
)

# 2. EKRAN VE TUVAL YAPILANDIRMASI
WIDTH, HEIGHT = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

# Çizimlerin yapılacağı kalıcı tuval
canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

# 3. RENK VE TASARIM AYARLARI
COLORS = [
    (255, 0, 0),    # Mavi
    (0, 255, 0),    # Yeşil
    (0, 0, 255),    # Kırmızı
    (0, 255, 255),  # Sarı
    (0, 0, 0)       # Silgi (Siyah)
]
last_selected_color = COLORS[1] # En son seçilen geçerli renk
current_color = COLORS[1]       # Aktif renk
brush_thickness = 10            # Daha zarif ince bir fırça
eraser_thickness = 100

# Gökkuşağı El Renkleri (21 Nokta İçin)
def get_rainbow_palette(n=21):
    palette = []
    for i in range(n):
        hue = i / n
        rgb = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
        bgr = (int(rgb[2]*255), int(rgb[1]*255), int(rgb[0]*255))
        palette.append(bgr)
    return palette

RAINBOW_PALETTE = get_rainbow_palette(21)
BG_COLOR = (15, 10, 20) # Çok koyu mor/siyah bazlı arkaplan

# Çizim değişkenleri
px, py = 0, 0 # Önceki koordinatlar
tip_ids = [4, 8, 12, 16, 20]

print("🚀 Hassas Air Canvas Başlatıldı! Çıkmak için 'q' basın.")

while True:
    # 4. GÖRÜNTÜ AL VE ÖN İŞLEME
    success, frame = cap.read()
    if not success: break
    frame = cv2.flip(frame, 1)
    
    # KULLANICIYI GİZLE: Şık bir dijital ortam oluştur
    display_frame = np.full((HEIGHT, WIDTH, 3), BG_COLOR, dtype=np.uint8)

    # 5. ÜST MENÜ (RENK SEÇİM PANELİ)
    # Tasarımı daha modern ve ince yapalım
    cv2.rectangle(display_frame, (10, 5), (250, 60), (255, 0, 0), cv2.FILLED)
    cv2.rectangle(display_frame, (260, 5), (500, 60), (0, 255, 0), cv2.FILLED)
    cv2.rectangle(display_frame, (510, 5), (750, 60), (0, 0, 255), cv2.FILLED)
    cv2.rectangle(display_frame, (760, 5), (1000, 60), (0, 255, 255), cv2.FILLED)
    cv2.rectangle(display_frame, (1010, 5), (1270, 60), (200, 200, 200), cv2.FILLED)
    cv2.putText(display_frame, "TEMIZLE/SIL", (1070, 40), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 2)

    # 6. MEDIAPIPE ANALİZİ
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                lm_list.append([id, int(lm.x * WIDTH), int(lm.y * HEIGHT)])

            if lm_list:
                # Önemli landmarklar
                x1, y1 = lm_list[8][1], lm_list[8][2]   # İşaret parmağı ucu
                x2, y2 = lm_list[12][1], lm_list[12][2]  # Orta parmak ucu

                # Parmak kontrolleri
                fingers = []
                # Baş parmak
                if lm_list[4][1] > lm_list[3][1]: fingers.append(1)
                else: fingers.append(0)
                # Diğer 4 parmak
                for i in range(1, 5):
                    if lm_list[tip_ids[i]][2] < lm_list[tip_ids[i] - 2][2]: fingers.append(1)
                    else: fingers.append(0)

                # --- KRİTİK MANTIK: SIRALAMA ÇOK ÖNEMLİ ---

                # A. MENÜ BÖLGESİ (Seçim)
                if y1 < 60:
                    px, py = 0, 0 # Çizgiyi kes
                    if 10 < x1 < 250: 
                        current_color = COLORS[0]
                        last_selected_color = COLORS[0]
                    elif 260 < x1 < 500: 
                        current_color = COLORS[1]
                        last_selected_color = COLORS[1]
                    elif 510 < x1 < 750: 
                        current_color = COLORS[2]
                        last_selected_color = COLORS[2]
                    elif 760 < x1 < 1000: 
                        current_color = COLORS[3]
                        last_selected_color = COLORS[3]
                    elif 1010 < x1 < 1270: 
                        # Menüden silgi seçildiğinde tuvali temizleme gibi düşünebiliriz
                        # Ya da fırçayı siyah yapabiliriz
                        current_color = (0,0,0)

                # B. DURAKLATMA (5 Parmak Birden) - ÖNCELİKLİ MOD
                elif fingers.count(1) == 5:
                    px, py = 0, 0 # Koordinatları takip et ama çizme

                # C. SİLGİ MODU (İşaret + Orta Parmak Açık = V İŞARETİ)
                elif fingers[1] == 1 and fingers[2] == 1:
                    # Silgi modunda ekranda geri bildirim ver
                    cv2.rectangle(display_frame, (x1-30, y1-30), (x1+30, y1+30), (255, 255, 255), 2)
                    
                    if px != 0 and py != 0:
                        # Silgiyi sürekli çizgi halinde kullan (kopmasın)
                        cv2.line(canvas, (px, py), (x1, y1), (0,0,0), eraser_thickness)
                    
                    px, py = x1, y1

                # D. ÇİZİM MODU (Sadece İşaret Parmağı Açık)
                elif fingers[1] == 1:
                    # Eğer orta parmak kapalıysa gerçek çizim modundayız demektir
                    # (Hassasiyet için serçe ve yüzük parmağının durumuna bakmıyoruz, 
                    # sadece orta parmak kapalı olmalı)
                    if fingers[2] == 0:
                        # Rengi geri getir (Eğer silgiden geldiysek)
                        if current_color == (0,0,0):
                            current_color = last_selected_color
                        
                        # Ekranda fırça ucunu göster
                        cv2.circle(display_frame, (x1, y1), 8, current_color, cv2.FILLED)

                        if px == 0 and py == 0:
                            px, py = x1, y1
                        
                        # Mesafe Kontrolü: Hızlı hareketlerde çizgi çek, çok uzaksa çekme
                        dist = np.hypot(x1 - px, y1 - py)
                        if dist < 80: # 80 pikselden fazla atlama varsa kopukluk olur
                            cv2.line(canvas, (px, py), (x1, y1), current_color, brush_thickness)
                        
                        px, py = x1, y1
                    else:
                        # Diğer durumlarda çizimi kes (Elimiz havadayken gezme modu)
                        px, py = 0, 0
                
                else:
                    # El algılanıyor ama tanımlı bir modda değilse çizimi kes
                    px, py = 0, 0

            # --- DİJİTAL GÖKKUŞAĞI EL ÇİZİMİ ---
            mp_drawing.draw_landmarks(
                display_frame, hand_lms, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,0,0), thickness=0), 
                mp_drawing.DrawingSpec(color=(80, 80, 100), thickness=1)
            )
            for id, lm in enumerate(hand_lms.landmark):
                cx, cy = int(lm.x * WIDTH), int(lm.y * HEIGHT)
                cv2.circle(display_frame, (cx, cy), 5, RAINBOW_PALETTE[id], cv2.FILLED)

    # 7. GÖRÜNTÜLERİ BİRLEŞTİRME VE SÜREKLİLİK
    img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, img_inv = cv2.threshold(img_gray, 5, 255, cv2.THRESH_BINARY_INV)
    img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
    
    display_frame = cv2.bitwise_and(display_frame, img_inv)
    display_frame = cv2.bitwise_or(display_frame, canvas)

    # Köşeye zarif bir imza
    cv2.putText(display_frame, "Air Canvas V2 | Hassas Cizim Modu", (40, HEIGHT-30), 
                cv2.FONT_HERSHEY_DUPLEX, 0.5, (100, 100, 150), 1)

    # 8. GÖSTER
    cv2.imshow("Air Canvas V2: Future Edition", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
