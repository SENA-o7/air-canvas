# ---------------------------------------------------------
# DERS 1: Gökkuşağı Landmarks (21 Nokta - 21 Farklı Renk)
# ---------------------------------------------------------
# Bu ders, MediaPipe kütüphanesinin el haritalama sistemini
# en renkli haliyle öğretir. Ekrandaki her iki elin 21 
# landmark noktası, gökkuşağı spektrumundaki farklı 
# renklerle ve zarif ince çizgilerle görselleştirilir.
# ---------------------------------------------------------

import cv2
import mediapipe as mp
import colorsys

# 1. MediaPipe Çözümlerini Hazırla
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 2. Hands Nesnesini Yapılandır
# max_num_hands=2: Çift el desteği
hands = mp_hands.Hands(
    static_image_mode=False, 
    max_num_hands=2, 
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# 3. Gökkuşağı Renk Spektrumu Oluştur (21 Nokta için)
def get_rainbow_palette(n=21):
    palette = []
    for i in range(n):
        # HSV -> RGB -> BGR (Zariflik için doygunluk 0.7, parlaklık 1.0)
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

# Çizim Stilleri
line_style = mp_drawing.DrawingSpec(color=(220, 220, 220), thickness=1, circle_radius=1)


while cap.isOpened():
    success, img = cap.read()
    if not success: break

    img = cv2.flip(img, 1) # Ayna modu
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            # Önce bağlantı çizgilerini (iskeleti) çok ince ve beyazımsı çizelim
            mp_drawing.draw_landmarks(
                img, 
                hand_lms, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,0,0), thickness=0), # Noktaları burada çizmiyoruz
                line_style # İnce iskelet çizgileri
            )

            # Şimdi 21 noktayı (landmarks)  tek tek ekleyelim
            h, w, c = img.shape
            for id, lm in enumerate(hand_lms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                
                # Her ID için özel gökkuşağı rengi
                point_color = RAINBOW_PALETTE[id]
                
                # Zarif küçük daireler
                cv2.circle(img, (cx, cy), 5, point_color, cv2.FILLED)
                cv2.circle(img, (cx, cy), 7, (255, 255, 255), 1) # Beyaz dış çerçeve

    # --- ÜST PANEL (Zarif Tasarım) ---
    overlay = img.copy()
    cv2.rectangle(overlay, (40, 20), (450, 80), (255, 245, 255), cv2.FILLED)
    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
    cv2.putText(img, "Ders 1:  Landmarks ", (60, 55),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, (120, 50, 150), 1)

    cv2.imshow("Air Canvas ", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
