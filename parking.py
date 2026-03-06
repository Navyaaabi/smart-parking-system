import cv2

def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Clicked at:", x, y)

cap = cv2.VideoCapture("parking.mp4")

ret, frame = cap.read()

if not ret:
    print("Error loading video")
    exit()

cv2.imshow("Frame - Click Slots", frame)
cv2.setMouseCallback("Frame - Click Slots", mouse_click)

print("Click top-left and bottom-right of each slot.")
print("Press any key to exit.")

cv2.waitKey(0)
cv2.destroyAllWindows()