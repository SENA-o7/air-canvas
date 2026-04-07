import cv2
import mediapipe as mp
import numpy as np
import math
import random

"""
 RAMADAN PAINTER
-------------------------------------------------
Özellikler:
1. Ultra Neon Altın El: Göz alıcı parlaklıkta el landmarks.
2. Serçe Parmağı Hilal Modu: Serçe parmağınızı açtığınızda parmağınızın ucunda Hilal belirir.
3. Hassas Kalem: İşaret parmağı ile ultra akıcı çizim.
4. Silgi Modu: İşaret ve orta parmak açıkken (V işareti) siler.
5. Yıldız Yağmuru: Sol el açıldığında gökyüzünden yıldızlar dökülür.
-------------------------------------------------
"""


# 1. KURULUM
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

WIDTH, HEIGHT = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

# Katmanlar
canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
star_particles = [] # Yıldız yağmuru listesi

# ULTRA NEON RENKLER
GOLD_NEON = (0, 230, 255)      # Daha ateşli neon altın
GOLD_GLOW = (180, 255, 255)    # Beyaz-Sarı parlama
LANDMARK_COLOR = (50, 255, 255) # El noktaları için ultra neon

# Çizim değişkenleri
px, py = 0, 0
tip_ids = [4, 8, 12, 16, 20]
moon_ready = True # Ay çizimi için tetikleyici hazır mı?

# ---  MATEMATİKSEL ŞEKİL FONKSİYONLARI ---

def draw_moon_math(img, x, y, r=70):
    """Math mantığıyla ultra parlak bir Hilal çizer."""
    # Parlama efekti
    cv2.circle(img, (x, y), r+5, GOLD_NEON, 2, cv2.LINE_AA)
    # İç dolgu
    cv2.circle(img, (x, y), r, GOLD_GLOW, -1, cv2.LINE_AA)
    # Hilal kesiği
    cv2.circle(img, (x + int(r*0.45), y), int(r*0.95), (0, 0, 0), -1, cv2.LINE_AA)

def add_star_shower(particles):
    """Yıldız yağmuru ekler."""
    particles.append({
        "x": random.randint(0, WIDTH),
        "y": 0,
        "speed": random.randint(7, 15),
        "size": random.randint(1, 4)
    })



while True:
    success, frame = cap.read()
    if not success: break
    frame = cv2.flip(frame, 1)

    # Ekranı Şeffaf Karart
    overlay = np.zeros_like(frame)
    frame = cv2.addWeighted(frame, 0.4, overlay, 0.6, 0)

    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if results.multi_hand_landmarks:
        for idx, hand_handedness in enumerate(results.multi_handedness):
            label = hand_handedness.classification[0].label # 'Left' veya 'Right'
            hand_lms = results.multi_hand_landmarks[idx]
            
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                lm_list.append([id, int(lm.x * WIDTH), int(lm.y * HEIGHT)])

            if lm_list:
                x1, y1 = lm_list[8][1], lm_list[8][2]   # İşaret
                x2, y2 = lm_list[12][1], lm_list[12][2]  # Orta
                xs, ys = lm_list[20][1], lm_list[20][2]  # Serçe

                # Parmak durumları
                fingers = []
                for i in range(1, 5):
                    if lm_list[tip_ids[i]][2] < lm_list[tip_ids[i] - 2][2]: fingers.append(1)
                    else: fingers.append(0)

                # --- 🎨 SAĞ EL KONTROLLERİ ---
                if label == "Right":
                    # 1. YUMRUK (Dur)
                    if fingers.count(1) == 0:
                        px, py = 0, 0

                    # 2. AY ÇİZDİRME (Serçe Parmağı Açıldığında TEK SEFERLİK)
                    elif fingers[3] == 1:
                        px, py = 0, 0
                        if moon_ready:
                            draw_moon_math(canvas, xs, ys)
                            moon_ready = False # Parmağı kapatana kadar tekrar çizme
                        
                        cv2.circle(frame, (xs, ys), 15, GOLD_NEON, 2)
                        cv2.putText(frame, "AY EKLENDI", (xs+25, ys), cv2.FONT_HERSHEY_DUPLEX, 0.7, GOLD_GLOW, 1)

                    # 3. SİLGİ MODU (İşaret + Orta Parmak)
                    elif fingers[0] == 1 and fingers[1] == 1:
                        px, py = 0, 0
                        moon_ready = True # Mod değişince hazırla
                        cv2.circle(canvas, (x1, y1), 80, (0, 0, 0), -1)
                        cv2.rectangle(frame, (x1-40, y1-40), (x1+40, y1+40), (255,255,255), 2)

                    # 4. HASSAS ÇİZİM (Sadece İşaret, Serçe Kapalı)
                    elif fingers[0] == 1 and fingers[3] == 0:
                        if px == 0 and py == 0: px, py = x1, y1
                        if math.hypot(x1 - px, y1 - py) < 100:
                            cv2.line(canvas, (px, py), (x1, y1), GOLD_NEON, 10)
                            cv2.line(canvas, (px, py), (x1, y1), GOLD_GLOW, 2)
                        px, py = x1, y1
                        cv2.circle(frame, (x1, y1), 10, GOLD_GLOW, -1)
                    
                    else:
                        px, py = 0, 0
                        if fingers[3] == 0: moon_ready = True # Serçe kapandığında yeni ay için hazır ol

                # ---  SOL EL KONTROLLERİ ---
                if label == "Left":
                    if fingers.count(1) >= 2:
                        add_star_shower(star_particles)

            # ---  NEON LANDMARK ---
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS,
                                mp_draw.DrawingSpec(color=(0,0,0), thickness=0),
                                mp_draw.DrawingSpec(color=LANDMARK_COLOR, thickness=1))
            for id, lm in enumerate(hand_lms.landmark):
                cx, cy = int(lm.x * WIDTH), int(lm.y * HEIGHT)
                cv2.circle(frame, (cx, cy), 5, LANDMARK_COLOR, -1)

    # Yıldız Yağmuru
    updated = []
    for p in star_particles:
        p["y"] += p["speed"]
        if p["y"] < HEIGHT:
            cv2.circle(frame, (p["x"], p["y"]), p["size"], (255, 255, 255), -1)
            cv2.line(frame, (p["x"], p["y"]), (p["x"], p["y"]-15), GOLD_GLOW, 1)
            updated.append(p)
    star_particles = updated

    # Katman Birleştir
    img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, img_inv = cv2.threshold(img_gray, 5, 255, cv2.THRESH_BINARY_INV)
    img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, img_inv)
    frame = cv2.bitwise_or(frame, canvas)

    cv2.putText(frame, "ULTRA NEON RAMADAN PAINTER", (40, 40), 1, 1.5, GOLD_NEON, 2)
    cv2.imshow("Interactive Ramadan Art", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    if key == ord('c'): canvas[:] = 0

cap.release()
cv2.destroyAllWindows()
