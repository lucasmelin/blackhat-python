# Requires cv2 to be installed
# pip install opencv-python
import cv2
from pathlib import Path

ROOT = Path(__file__).parent / "pictures"
FACES = Path(__file__).parent / "faces"


def detect(srcdir: Path = ROOT, tgtdir: Path = FACES):
    for jpg in list(srcdir.glob("**/*.jpg")):
        fullname = srcdir / jpg.name
        newname = tgtdir / jpg.name
        img = cv2.imread(str(fullname))
        if img is None:
            # Image couldn't be read
            continue
        training = Path(__file__).parent / "haarcascade_frontalface_alt.xml"
        cascade = cv2.CascadeClassifier(str(training.resolve()))
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        try:
            rects = cascade.detectMultiScale(grey, 1.3, 5)
            if rects.any():
                print(f"Faces found in + {jpg.name}")
                rects[:, 2:] += rects[:, :2]
        except AttributeError:
            print(f"No faces found - {jpg.name}")
            continue
            # highlight the faces in the image
        for x1, y1, x2, y2 in rects:
            cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
        cv2.imwrite(str(newname), img)


if __name__ == "__main__":
    detect()
