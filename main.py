import cv2
import mediapipe as mp
import numpy as np

# ------------------- YENİ VERSİYON KURULUM -------------------
# MediaPipe el dedektörünü oluştur - YENİ VERSİYON SINTAKSI
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Hands nesnesini oluştur
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=0  # 0=en hafif, 1=daha doğru ama yavaş
)

# Kamera başlat
cap = cv2.VideoCapture(0)

# Kamera çözünürlüğünü al
_, frame = cap.read()
height, width, _ = frame.shape
canvas = np.zeros((height, width, 3), dtype=np.uint8)

# Çizim rengi
draw_color = (0, 255, 0)  # Yeşil

# Çizim değişkenleri
px, py = 0, 0

print("🎨 Air Canvas başlatıldı! Çıkmak için 'q' tuşuna basın.")

while True:
    success, frame = cap.read()
    if not success:
        print("Kamera okunamıyor!")
        break

    # Görüntüyü yansıt (ayna efekti)
    frame = cv2.flip(frame, 1)

    # MediaPipe RGB formatı ister
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb.flags.writeable = False

    # El tespiti yap
    results = hands.process(frame_rgb)

    # Tekrar BGR'ye çevir
    frame_rgb.flags.writeable = True
    frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # El noktalarını çiz
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

            # İşaret parmağı ucu (8 numaralı landmark)
            index_tip = hand_landmarks.landmark[8]

            # Koordinatları pixel değerine çevir
            x = int(index_tip.x * width)
            y = int(index_tip.y * height)

            # Noktayı daire içine al
            cv2.circle(frame, (x, y), 15, draw_color, -1)
            cv2.circle(frame, (x, y), 20, (255, 255, 255), 2)  # Beyaz çerçeve

            # Eğer önceki nokta varsa, çizgi çek
            if px != 0 and py != 0:
                # Mesafe kontrolü (çok uzak atlamaları engelle)
                distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
                if distance < 100:  # Maksimum 100 pixel atlama
                    cv2.line(canvas, (px, py), (x, y), draw_color, 8)

            px, py = x, y
    else:
        # El yoksa çizimi bekleme moduna al
        px, py = 0, 0

    # Tuvali ve kamerayı birleştir
    # Canvas'ı biraz saydam yap
    canvas_copy = canvas.copy()
    canvas_copy = cv2.addWeighted(canvas_copy, 0.5, np.zeros_like(canvas_copy), 0.5, 0)

    # Frame'e canvas'ı ekle
    frame_with_canvas = cv2.addWeighted(frame, 0.7, canvas_copy, 0.3, 0)

    # Bilgi yazısı ekle
    cv2.putText(frame_with_canvas, "Air Canvas - Parmaginizla cizin",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame_with_canvas, "Cikis: 'q'",
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    # Göster
    cv2.imshow('Air Canvas - Cizim', frame_with_canvas)
    cv2.imshow('Canvas - Tuval', canvas)  # Sadece tuvale bak

    # Çıkış
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Temizlik
cap.release()
cv2.destroyAllWindows()
print("👋 Program sonlandırıldı!")