"""
Bu Python betiği, hareket algılama sistemini, gece ve kızılötesi görüş efektlerini,
Discord Webhook entegrasyonunu ve sesli uyarıları içerir.

Kısıtlı Kullanım Lisansı

Telif Hakkı (c) [2023], [LuX]

Bu yazılımın kopyalarını almak için izin verilir ve sadece bu yazılımın kullanımına izin verilir
düzenlemek, birleştirmek, yayımlamak, dağıtmak, alt lisanslamak ve / veya satmak kesinlikle
yasaktır.

BU YAZILIM "OLDUĞU GİBİ" ESASINA GÖRE TEMİN EDİLMİŞ OLUP, HİÇBİR TÜRDE, AÇIK
VEYA ZIMNİ GARANTİLER DAHİL ANCAK BUNUNLA SINIRLI OLMAKSIZIN PAZARLANABİLİRLİK,
BELİRLİ BİR AMACA UYGUNLUK VEYA İHLAL OLMAMASI DAHİL ANCAK BUNUNLA SINIRLI
OLMAKSIZIN HİÇBİR GARANTİ VERİLMEMEKTEDİR. HİÇBİR DURUMDA YAZARLAR VEYA TELİF
SAHİPLERİ HİÇBİR TALEP, ZARAR VEYA DİĞER YÜKÜMLÜLÜKLERDEN SORUMLU DEĞİLDİR VE
YAZILIM KULLANIMI YA DA DİĞER ANLAŞMALARLA İLGİLİ HERHANGİ BİR KONUDA HİÇBİR
SORUMLULUK KABUL ETMEZ.
"""

import cv2
import numpy as np
import winsound
import time
import datetime
import requests
import os
import io
import json

print("Senforx Sensor Camera (SSC) programına hoşgeldiniz!")
print("Geliştirici: LuX")
print("Şu anda geliştirme aşamasında")

def apply_night_vision_effect(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.equalizeHist(frame)
    return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

def apply_infrared_vision_effect(frame):
    return cv2.applyColorMap(frame, cv2.COLORMAP_HOT)

valid_passwords = ["yoneticiucbesyedi", "everyone", "bakimmodu"]

while True:
    user_password = input("Şifreyi girin: ")
    if user_password in valid_passwords:
        if user_password == "yoneticiucbesyedi":
            print("Hoşgeldiniz LuX")
        elif user_password == "everyone":
            print("Hoşgeldiniz Kullanıcı!")
        else:
            print("Hoşgeldiniz Bakım Modu Kullanıcısı!")
        break
    else:
        print("Yanlış şifre! Tekrar deneyin veya programı kapatın.")

use_webhook = input("Webhook kullanmak istiyor musun? (Evet: E / Hayır: H): ")

if use_webhook.upper() == "E":
    webhook_url = input("Discord Webhook URL'sini girin: ")
else:
    webhook_url = None

use_night_vision = input("Gece görüş modunu etkinleştirmek istiyor musunuz? (Evet: E / Hayır: H): ")

use_infrared_vision = input("Kızılötesi görüş modunu etkinleştirmek istiyor musunuz? (Evet: E / Hayır: H): ")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Aygıt bağlı değil")
    kamera_durumu = "Aygıt bağlı değil"
else:
    kamera_durumu = "Aygıt bağlı"

print(f"Kamera Bağlantı Durumu: {kamera_durumu}")

if kamera_durumu == "Aygıt bağlı":
    motion_threshold = 1000

    previous_frame = None

    sound_file = "sound.mp3"

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Kamera okunamadı!")
            break

        if use_night_vision.upper() == "E":
            frame = apply_night_vision_effect(frame)
        elif use_infrared_vision.upper() == "E":
            frame = apply_infrared_vision_effect(frame)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (25, 25), 0)

        if previous_frame is None:
            previous_frame = gray_frame
            continue

        frame_delta = cv2.absdiff(previous_frame, gray_frame)
        thresh = cv2.threshold(frame_delta, 30, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False

        for contour in contours:
            if cv2.contourArea(contour) > motion_threshold:
                motion_detected = True

                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                break

        if motion_detected:
            winsound.PlaySound(sound_file, winsound.SND_ASYNC)

            if webhook_url:
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                screenshot_filename = f"screenshot_{timestamp}.png"
                cv2.imwrite(screenshot_filename, frame)

                with open(screenshot_filename, "rb") as f:
                    screenshot_data = io.BytesIO(f.read())

                payload = {
                    "content": "Hareket algılandı! Dikkatli olun.",
                    "username": "Hareket Algılama Botu"
                }
                files = {"file": ("screenshot.png", screenshot_data)}
                response = requests.post(webhook_url, data=payload, files=files)

                if response.status_code == 204:
                    print("Webhook'a mesaj ve ekran görüntüsü gönderildi.")
                    os.remove(screenshot_filename)

            time.sleep(2)

        previous_frame = gray_frame.copy()

        if use_infrared_vision.upper() == "E":
            thermal_frame = apply_infrared_vision_effect(gray_frame)
            cv2.imshow("Infrared Vision", thermal_frame)
        else:
            cv2.imshow("Motion Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("Programı kapatmak için herhangi bir tuşa basın...")
    input()
