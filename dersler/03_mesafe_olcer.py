# ---------------------------------------------------------
# DERS 3: Estetik Mesafe Ölçümü (Hassas & Zarif Tasarım)
# ---------------------------------------------------------
# Bu ders, iki parmak ucu arasındaki mesafeyi ölçerek 
# "tıklama" veya "seçme" gibi interaktif eylemleri nasıl 
# kontrol edeceğimizi öğretir.
# ---------------------------------------------------------

import cv2
import mediapipe as mp
import math
import numpy as np

# MediaPipe Yapılandırması
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Kamera Ayarları
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# --- ESTETİK RENK PALETİ ---
COLOR_PINK = (220, 180, 255)    # Yumuşak Pembe (Noktalar için)
COLOR_PURPLE = (150, 80, 200)   # Zarif Mor (Çizgiler için)
COLOR_BG_LITE = (255, 245, 250) # Çok Açık Pembe (Panel için)
COLOR_TEXT = (100, 50, 150)     # Derin Mor (Yazılar için)
COLOR_SUCCESS = (150, 230, 150) # Başarı Yeşili (Tıklama anı)

def draw_info_box(img, length, is_clicked):
    """Ekrana zarif bir mesafe bilgi kutusu çizer."""
    overlay = img.copy()
    box_color = COLOR_BG_LITE if not is_clicked else COLOR_SUCCESS
    
    # Bilgi kutusu (Yarı saydam)
    cv2.rectangle(overlay, (50, 50), (350, 150), box_color, cv2.FILLED)
    cv2.rectangle(overlay, (50, 50), (350, 150), COLOR_PURPLE, 1) # İnce sınır
    
    img = cv2.addWeighted(overlay, 0.6, img, 0.4, 0)
    
    # Yazılar
    status = "TIKLAMA AKTIF" if is_clicked else "MESAFE OLCULUYOR"
    cv2.putText(img, status, (70, 85), cv2.FONT_HERSHEY_DUPLEX, 0.6, COLOR_TEXT, 1)
    cv2.putText(img, f"{int(length)} px", (70, 130), cv2.FONT_HERSHEY_DUPLEX, 1.2, COLOR_TEXT, 2)
    return img

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    length = 0
    is_clicked = False

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                lm_list.append([id, int(lm.x * w), int(lm.y * h)])

            if lm_list:
                # Baş parmak ucu (4) ve İşaret parmağı ucu (8)
                x1, y1 = lm_list[4][1], lm_list[4][2]
                x2, y2 = lm_list[8][1], lm_list[8][2]
                
                # Orta noktayı bul
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                # İki nokta arasındaki mesafe (Öklid)
                length = math.hypot(x2 - x1, y2 - y1)
                
                # Tasarım: Kibar çizgiler ve noktalar
                # Bağlantı çizgisi
                line_thickness = 2 if length > 40 else 4
                cv2.line(img, (x1, y1), (x2, y2), COLOR_PURPLE, line_thickness)
                
                # Parmak uçlarındaki küçük halkalar
                cv2.circle(img, (x1, y1), 8, COLOR_PINK, cv2.FILLED)
                cv2.circle(img, (x1, y1), 12, COLOR_PURPLE, 1)
                cv2.circle(img, (x2, y2), 8, COLOR_PINK, cv2.FILLED)
                cv2.circle(img, (x2, y2), 12, COLOR_PURPLE, 1)

                # Tıklama kontrolü (Mesafe eşiği)
                if length < 40:
                    is_clicked = True
                    # Tıklama anında orta noktada parlayan bir efekt
                    cv2.circle(img, (cx, cy), 15, COLOR_SUCCESS, cv2.FILLED)
                    cv2.circle(img, (cx, cy), 20, (255, 255, 255), 2)
                else:
                    # Normal durumda orta nokta
                    cv2.circle(img, (cx, cy), 6, COLOR_PURPLE, cv2.FILLED)

            # El iskeletini çok ince ve zarif çiz
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS,
                                 mp_draw.DrawingSpec(color=COLOR_PINK, thickness=1, circle_radius=1),
                                 mp_draw.DrawingSpec(color=COLOR_PURPLE, thickness=1, circle_radius=1))

    # Arayüzü güncelle
    img = draw_info_box(img, length, is_clicked)

    cv2.imshow("Ders 3:  Mesafe Olcer", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
