import io
import os
import subprocess
import shutil
from glob import glob

import torch
from cloudinary import uploader
from PIL import Image
import base64
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from detections.serializers import CariesDetectionSerializer


def image_to_byte_array(image: Image) -> bytes:
    byte_array = io.BytesIO()
    image.save(byte_array, format="JPEG")
    byte_array = byte_array.getvalue()
    return byte_array


class CariesDetectionView(CreateAPIView):
    """
    post: Returns the url strings of the pictures with caries data.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CariesDetectionSerializer

    def create(self, request, *args, **kwargs):
        """
        Register a new dental diagnosis.
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            response = {"denture_images": []}
            worker = os.getpid()
            denture_images = serializer.validated_data["denture_images"]
            try:
                for indx, image in enumerate(denture_images):
                    filename = f"/home/ubuntu/dentasis/detections/detect/{worker}/{indx}.png"
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, "wb") as f:
                        f.write(base64.b64decode(image))
                        f.close()

                subprocess.run(["/home/ubuntu/dentasis/venv/bin/python", "/home/ubuntu/dentasis/detections/yolov7/detect.py", "--no-trace", "--save-txt", "--save-conf", "--conf-thres", "0.1", "--img-size", "640", "--weights", "/home/ubuntu/dentasis/detections/model.pt", "--source", f"/home/ubuntu/dentasis/detections/detect/{worker}", "--name", f"/home/ubuntu/dentasis/detections/runs/detect/{worker}"])

                for detection in glob(f"/home/ubuntu/dentasis/detections/runs/detect/{worker}/*.*"): 
                    pre, _ = os.path.splitext(detection)
                    image = pre + ".jpeg"
                    head, tail = os.path.split(detection)
                    results = head + "/labels/" + tail.split(".")[0] + ".txt"
                    old_image = Image.open(detection)
                    new_image = old_image.convert("RGB")
                    new_image.save(image, quality=50, optimize=True)

                    with open(image, "rb") as f:
                        encoded_image = base64.b64encode(f.read()).decode("UTF-8")
                        cloudinary_response = uploader.upload(
                            "data:image/jpeg;base64," + encoded_image
                        )
                        f.close()

                    confs = []
                    try:
                        with open(results) as f:
                            confs = [l.rsplit(" ")[-1].strip() for l in f]
                            confs.reverse()
                            confs = [f"{float(r):.2f}" for r in confs]
                            f.close()
                    except:
                        pass

                    response["denture_images"].append(
                        {
                            "image_url": cloudinary_response["url"],
                            "confidence": confs,
                        }
                    )
            finally:
                shutil.rmtree(f"/home/ubuntu/dentasis/detections/detect/{worker}")
                shutil.rmtree(f"/home/ubuntu/dentasis/detections/runs/detect/{worker}")
            return Response(response, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
