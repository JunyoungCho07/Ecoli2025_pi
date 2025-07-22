import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Windows는 DirectShow 가산 옵션
if not cap.isOpened():
    raise IOError("카메라 열기 실패")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("USB Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
