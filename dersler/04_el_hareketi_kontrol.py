# ---------------------------------------------------------
# DERS 4: Detaylı El Hareketleri (Renk Kodlu & Zarif Tasarım)
# ---------------------------------------------------------
# Bu ders, MediaPipe landmark numaralarını öğrenmeyi ve her 
# parmağı ayrı ayrı kontrol etmeyi öğretir.
# ---------------------------------------------------------

import cv2
import mediapipe as mp
import numpy as np

# MediaPipe Kurulumu
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Kamera Ayarları
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# --- ESTETİK RENK KODLARI ---
# Her parmak için ayrı bir "kibar" renk tanımlayalım
FINGER_COLORS = {
    "Thumb": (255, 180, 230),  # Soft Pembe
    "Index": (180, 150, 250),  # Soft Lila
    "Middle": (150, 230, 250), # Soft Mavi
    "Ring": (150, 250, 200),   # Soft Yeşil
    "Pinky": (250, 230, 150)   # Soft Sarı
}
COLOR_BG = (245, 235, 255)     # Panel Arkaplan
COLOR_TEXT = (90, 40, 120)     # Metin Rengi

# Parmak Landmark Grupları
LANDMARK_GROUPS = {
    "Thumb": [0, 1, 2, 3, 4],
    "Index": [5, 6, 7, 8],
    "Middle": [9, 10, 11, 12],
    "Ring": [13, 14, 15, 16],
    "Pinky": [17, 18, 19, 20]
}

def get_gesture_name(fingers):
    """Parmakların durumuna göre hareket adını döndürür."""
    if all(f == 0 for f in fingers):
        return "Yumruk Modu"
    if all(f == 1 for f in fingers):
        return "Tum El Acik"
    if fingers == [0, 1, 1, 0, 0]:
        return "Iki Parmak (V Isareti)"
    if fingers == [0, 1, 0, 0, 0]:
        return "Isaret Parmagi (Kalem)"
    if fingers == [0, 0, 1, 0, 0]:
        return "Orta Parmak"
    if fingers == [0, 0, 0, 1, 0]:
        return "Yuzuk Parmagi"
    if fingers == [0, 0, 0, 0, 1]:
        return "Serce Parmak"
    if fingers == [1, 0, 0, 0, 0]:
        return "Bas Parmak"
    return "Karisik Hareket"

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    gesture_text = "El Bekleniyor..."
    
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                lm_list.append([id, int(lm.x * w), int(lm.y * h)])

            if lm_list:
                # Parmak Durumlarını Hesapla
                fingers = []
                # Baş parmak (Yatay)
                if lm_list[4][1] > lm_list[3][1]: fingers.append(1)
                else: fingers.append(0)
                # Diğer 4 parmak (Dikey)
                for i in [8, 12, 16, 20]:
                    if lm_list[i][2] < lm_list[i-2][2]: fingers.append(1)
                    else: fingers.append(0)

                gesture_text = get_gesture_name(fingers)

                # --- ÖZEL ÇİZİM (Her Parmak Kendi Rengiyle) ---
                for finger_name, ids in LANDMARK_GROUPS.items():
                    color = FINGER_COLORS[finger_name]
                    # Boğumları ve uçları çiz
                    for i in ids:
                        cv2.circle(img, (lm_list[i][1], lm_list[i][2]), 6, color, cv2.FILLED)
                    # İlgili parmağın bağlantılarını çiz
                    for i in range(len(ids)-1):
                        cv2.line(img, (lm_list[ids[i]][1], lm_list[ids[i]][2]), 
                                 (lm_list[ids[i+1]][1], lm_list[ids[i+1]][2]), color, 3)

    # --- ZARİF MOD PANELİ ---
    overlay = img.copy()
    cv2.rectangle(overlay, (40, 40), (450, 160), COLOR_BG, cv2.FILLED)
    cv2.rectangle(overlay, (40, 40), (450, 160), COLOR_TEXT, 1)
    img = cv2.addWeighted(overlay, 0.4, img, 0.6, 0)
    
    cv2.putText(img, "HAREKET ANALIZI", (60, 80), cv2.FONT_HERSHEY_DUPLEX, 0.7, COLOR_TEXT, 1)
    cv2.putText(img, gesture_text, (60, 130), cv2.FONT_HERSHEY_DUPLEX, 1.0, COLOR_TEXT, 2)

    cv2.imshow("Ders 4:  Hareket Kontrolu", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
