# ---------------------------------------------------------
# DERS 2: Gelişmiş Parmak Sayma (Çoklu El & Zarif Tasarım)
# ---------------------------------------------------------
# Bu ders, MediaPipe ile ekrandaki tüm elleri algılamayı ve 
# parmak sayılarını estetik bir arayüzle sunmayı öğretir.

# ---------------------------------------------------------

import cv2
import mediapipe as mp
import numpy as np

# MediaPipe Ayarları
mp_hands = mp.solutions.hands
# max_num_hands=4: Ekrandaki 4 ele kadar hepsini birlikte sayar.
hands = mp_hands.Hands(max_num_hands=4, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Kamera Hazırlığı
cap = cv2.VideoCapture(0)
cap.set(3, 1280) # Genişlik
cap.set(4, 720)  # Yükseklik

# Parmak uçları ID'leri (MediaPipe standartları)
tip_ids = [4, 8, 12, 16, 20]

# --- ESTETİK RENK PALETİ ---
COLOR_BG = (245, 235, 255)      # Soft Lila Arkaplan
COLOR_TEXT = (90, 40, 120)      # Derin Mor Metin
COLOR_ACCENT = (200, 100, 220)  # Vurgu Rengi (Pembe-Mor)
COLOR_HANDS = (255, 180, 230)   # El Bağlantı Rengi (Soft Pembe)

def draw_stylish_panel(img, total_count):
    """Ekrana zarif bir bilgi paneli çizer."""
    overlay = img.copy()
    # Panel kutusu
    cv2.rectangle(overlay, (40, 40), (420, 160), COLOR_BG, cv2.FILLED)
    # Yumuşak bir çerçeve
    cv2.rectangle(overlay, (40, 40), (420, 160), COLOR_ACCENT, 2)
    
    # Saydamlık uygula
    cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)
    
    # Bilgileri Yazdır
    cv2.putText(img, "PARMAK ANALIZI", (60, 80), cv2.FONT_HERSHEY_DUPLEX, 0.7, COLOR_TEXT, 1)
    cv2.putText(img, f"Toplam Sayi: {total_count}", (60, 130), 
                cv2.FONT_HERSHEY_DUPLEX, 1.1, COLOR_TEXT, 2)

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1) # Ayna modu (Doğal hareket için)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    total_fingers = 0

    if results.multi_hand_landmarks:
        # Ekrandaki her bir el için işlem yap
        for hand_lms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

            if lm_list:
                fingers = []

                # --- BAŞ PARMAK KONTROLÜ ---
                # Bilek ile baş parmak ucu arasındaki yatay mesafeye bakarız
                if lm_list[tip_ids[0]][1] > lm_list[tip_ids[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                # --- DİĞER 4 PARMAK KONTROLÜ ---
                for i in range(1, 5):
                    # Parmak ucu eklemden daha yukarıdaysa (Y koordinatı küçükse) açıktır
                    if lm_list[tip_ids[i]][2] < lm_list[tip_ids[i] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                total_fingers += fingers.count(1)

            # El çizgilerini estetik renklerle çiz
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS,
                                 mp_draw.DrawingSpec(color=COLOR_HANDS, thickness=3, circle_radius=3),
                                 mp_draw.DrawingSpec(color=COLOR_ACCENT, thickness=2, circle_radius=2))

    # Bilgi panelini ekrana yerleştir
    draw_stylish_panel(img, total_fingers)

    # --- SAYAÇ VE ANALİZ MANTIĞI ---
    if total_fingers >= 10:
        cift_el_sayisi = total_fingers // 10
        # Zarif bir analiz yazısı
        cv2.putText(img, f"Analiz: {cift_el_sayisi} Cift El Algilandi!", (450, 90), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, COLOR_ACCENT, 2)
        
        # Tam 10, 20 gibi katlarda özel kutlama
        if total_fingers % 10 == 0:
            cv2.putText(img, "Tam Uyum Saglandi!", (450, 140), 
                        cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1.2, COLOR_TEXT, 2)
    elif total_fingers > 0:
        cv2.putText(img, "Parmaklar Sayiliyor...", (450, 90), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, COLOR_TEXT, 1)

    cv2.imshow("Ders 2: Parmak Sayici", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
