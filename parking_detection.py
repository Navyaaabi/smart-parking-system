from ultralytics import YOLO
import cv2

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

video_path = "parking.mp4"
cap = cv2.VideoCapture(video_path)

# 🔥 YOUR 22 PARKING SLOTS
parking_slots = {

    # TOP ROW
    "slot1":  [(6,36), (112,266)],
    "slot2":  [(122,38), (229,267)],
    "slot3":  [(238,38), (341,265)],
    "slot4":  [(351,40), (458,265)],
    "slot5":  [(466,40), (575,267)],
    "slot6":  [(580,38), (691,267)],
    "slot7":  [(697,37), (806,266)],
    "slot8":  [(810,36), (923,265)],
    "slot9":  [(925,37), (1038,264)],
    "slot10": [(1041,38), (1155,266)],
    "slot11": [(1156,37), (1271,265)],
    "slot12": [(1269,36), (1387,266)],

    # BOTTOM ROW
    "slot13": [(21,594), (127,831)],
    "slot14": [(138,593), (243,831)],
    "slot15": [(255,593), (362,829)],
    "slot16": [(371,591), (480,828)],
    "slot17": [(488,592), (600,830)],
    "slot18": [(607,591), (718,829)],
    "slot19": [(724,593), (837,828)],
    "slot20": [(842,594), (954,830)],
    "slot21": [(958,592), (1074,829)],
    "slot22": [(1075,592), (1195,829)]
}

while True:
    ret, frame = cap.read()

    # 🔁 LOOP VIDEO
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    results = model(frame, imgsz=frame.shape[:2])

    # Reset all slots to empty
    slot_status = {key: False for key in parking_slots}
    print(slot_status)

    # Detect cars
    for r in results:
        for box in r.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            box_area = (x2 - x1) * (y2 - y1)

        # Ignore very small detections (removes phones etc.)
            if box_area < 5000:
                continue

        # Draw detected object
            cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0), 2)

            for slot, ((sx1, sy1), (sx2, sy2)) in parking_slots.items():

                if x1 < sx2 and x2 > sx1 and y1 < sy2 and y2 > sy1:
                    slot_status[slot] = True
                    
    # 🔥 DRAW SLOTS
    for slot, ((sx1, sy1), (sx2, sy2)) in parking_slots.items():

        if slot_status[slot]:
            color = (0, 0, 255)  # 🔴 Red (occupied)
        else:
            color = (0, 255, 0)  # 🟢 Green (empty)

        cv2.rectangle(frame, (sx1, sy1), (sx2, sy2), color, 3)

    cv2.imshow("Smart Parking Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()