# ---------------------------------------------------------
# DERS 5: Gökkuşağı Çoklu El Takibi (Sağ/Sol Ayrımı)
# ---------------------------------------------------------
# Bu ders, ekrandaki ellerin hangisinin sağ hangisinin sol 
# olduğunu anlamayı ve her iki eli de 21 ayrı gökkuşağı 
# rengiyle takip etmeyi öğretir.
# ---------------------------------------------------------

import cv2
import mediapipe as mp
import colorsys
import numpy as np

# 1. MediaPipe Çözümlerini Hazırla
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 2. Hands Nesnesini Yapılandır (max_num_hands=2)
hands = mp_hands.Hands(
    static_image_mode=False, 
    max_num_hands=2, 
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# 3. Gökkuşağı Renk Spektrumu Oluştur (21 Nokta için)
def get_rainbow_palette(n=21):
    palette = []
    for i in range(n):
        hue = i / n
        rgb = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
        bgr = (int(rgb[2]*255), int(rgb[1]*255), int(rgb[0]*255))
        palette.append(bgr)
    return palette

RAINBOW_PALETTE = get_rainbow_palette(21)

# 4. Kamera Hazırlığı
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Estetik Renkler
COLOR_BG = (255, 245, 255)
COLOR_TEXT = (120, 50, 150)
COLOR_ACCENT = (200, 100, 220)

def draw_hand_label(img, x, y, label, score):
    """Elin üzerine zarif bir Sağ/Sol etiketi yazar."""
    displayText = f"{'SAG' if label == 'Right' else 'SOL'} %{int(score*100)}"
    color = (150, 230, 150) if label == "Right" else (255, 180, 230)
    
    # Küçük bir etiket arkaplanı
    cv2.rectangle(img, (x-40, y+20), (x+100, y+60), (255,255,255), cv2.FILLED)
    cv2.rectangle(img, (x-40, y+20), (x+100, y+60), color, 1)
    cv2.putText(img, displayText, (x-30, y+50), cv2.FONT_HERSHEY_DUPLEX, 0.6, COLOR_TEXT, 1)

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1) # Ayna modu
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        # results.multi_handedness içerisinde Sağ/Sol bilgisi tutulur
        for idx, hand_handedness in enumerate(results.multi_handedness):
            label = hand_handedness.classification[0].label # 'Left' veya 'Right'
            score = hand_handedness.classification[0].score
            hand_lms = results.multi_hand_landmarks[idx]
            
            # --- ZARİF İSKELET ÇİZİMİ ---
            mp_drawing.draw_landmarks(
                img, hand_lms, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,0,0), thickness=0), # Noktaları manuel çizeceğiz
                mp_drawing.DrawingSpec(color=(220, 220, 220), thickness=1) # İnce çizgiler
            )

            # --- GÖKKUŞAĞI NOKTALARI ---
            h, w, c = img.shape
            for id, lm in enumerate(hand_lms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 5, RAINBOW_PALETTE[id], cv2.FILLED)
                cv2.circle(img, (cx, cy), 7, (255, 255, 255), 1)

            # Bilek koordinatına etiket ekle
            wrist_x = int(hand_lms.landmark[0].x * w)
            wrist_y = int(hand_lms.landmark[0].y * h)
            draw_hand_label(img, wrist_x, wrist_y, label, score)

    # --- ÜST ANALİZ PANELİ ---
    overlay = img.copy()
    cv2.rectangle(overlay, (40, 20), (450, 80), COLOR_BG, cv2.FILLED)
    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
    cv2.putText(img, "Ders 5:  Coklu El Takibi", (60, 55),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, COLOR_TEXT, 1)

    cv2.imshow("Air Canvas - Coklu El Egitimi", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
