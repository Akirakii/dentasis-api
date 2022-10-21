import io
import math
import os
import cv2
import shutil
from roboflow import Roboflow
import numpy as np

import torch
from cloudinary import uploader
from PIL import Image
import base64
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from detections.serializers import CariesDetectionSerializer


def toImgPIL(imgOpenCV): 
    return Image.fromarray(cv2.cvtColor(imgOpenCV, cv2.COLOR_BGR2RGB))

class CariesDetectionView(CreateAPIView):
    """
    post: Returns the url strings of the pictures with caries data.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CariesDetectionSerializer
    rf = Roboflow(api_key="mPC9t1ocnMZT3PGnsc9u")
    project = rf.workspace("dentasis").project("dentasisv2")
    model = project.version(2).model

    def create(self, request, *args, **kwargs):
        """
        Register a new dental diagnosis.
        """
        print("starting...")
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        print("validating...")
        if serializer.is_valid():
            response = {"denture_images": []}
            
            worker = os.getpid()
            print("processing images...")
            denture_images = serializer.validated_data["denture_images"]
            try:
                for indx, imagebytes in enumerate(denture_images):
                    filename = f"/home/ubuntu/dentasis/detections/detect/{worker}/{indx}.jpeg"
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    PIL_image = Image.open(io.BytesIO(base64.b64decode(imagebytes)))
                    width, height = PIL_image.size
                    max_size = 1000
                    if width > height and width > max_size: 
                        new_size = (max_size, int(height / (width / max_size)))
                        print("resizing to: ", new_size)
                        PIL_image = PIL_image.resize(new_size)
                    elif width < height and height > max_size: 
                        new_size = (int(width / (height / max_size)), max_size)
                        print("resizing to: ", new_size)
                        PIL_image = PIL_image.resize(new_size)

                    PIL_image.save(filename, quality=70, optimize=True)
                    print("created: ", filename)

                    print("starting predictions...")
                    prediction = self.model.predict(filename)
                    results = prediction.json()["predictions"]
                    print("processing results...")

                    confs = []
                    image = cv2.imread(filename)
                    stroke_color = (83, 12, 145)
                    w, h = PIL_image.size
                    stroke = int(math.ceil(w * h / 400000))
                    for result in results:
                        conf = float(result["confidence"])
                        confs.append(f"{conf:.2f}")
                        conf *= 100
                        conf = f"{conf:.2f}%"

                        width = result["width"]
                        height = result["height"]
                        x = result["x"]
                        y = result["y"]

                        cv2.rectangle(
                                image,
                                (int(x - width / 2), int(y + height / 2)),
                                (int(x + width / 2), int(y - height / 2)),
                                stroke_color,
                                stroke,
                            )

                        text_size = cv2.getTextSize(conf, cv2.FONT_HERSHEY_SIMPLEX, 0.4*stroke, 1*stroke)[0]
                        cv2.rectangle(
                                image,
                                (int(x - width / 2), int(y - height / 2)),
                                (
                                    int(x - width / 2 + text_size[0]),
                                    int(y - height / 2 - text_size[1]),
                                ),
                                stroke_color,
                                -1,
                            )
                        cv2.putText(
                                image,
                                conf,
                                (int(x - width / 2), int(y - height / 2)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.4*stroke,
                                (255, 255, 255),
                                thickness=stroke,
                            )
                    print("confs: ", confs)

                    _, tail = os.path.split(filename)
                    detected_filename = f"/home/ubuntu/dentasis/detections/detected/{worker}/" + tail
                    os.makedirs(os.path.dirname(detected_filename), exist_ok=True)
                    PIL_image = toImgPIL(image)
                    PIL_image.save(detected_filename)
                    print("created: ", detected_filename)
                    confs.sort(reverse=True)

                    with open(detected_filename, "rb") as f:
                        encoded_image = base64.b64encode(f.read()).decode("UTF-8")
                        cloudinary_response = uploader.upload(
                            "data:image/jpeg;base64," + encoded_image
                        )
                        f.close()

                    response["denture_images"].append(
                        {
                            "image_url": cloudinary_response["url"],
                            "confidence": confs,
                        }
                    )
            finally:
                shutil.rmtree(f"/home/ubuntu/dentasis/detections/detect/{worker}/")
                shutil.rmtree(f"/home/ubuntu/dentasis/detections/detected/{worker}/")
            return Response(response, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
