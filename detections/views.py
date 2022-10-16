import io

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
            denture_images = serializer.validated_data["denture_images"]
            response = {"denture_images": []}
            model = torch.hub.load(
                "detections/yolov7", "custom", "detections/model.pt", source="local"
            )
            model.conf=0.1
            model.eval()
            for image in denture_images:
                img = Image.open(io.BytesIO(base64.b64decode(image)))
                results = model([img], size=640)
                result_image = results.render()[0]
                encoded_result_image = base64.b64encode(
                    image_to_byte_array(result_image)
                ).decode("UTF-8")
                cloudinary_response = uploader.upload(
                    "data:image/jpeg;base64," + encoded_result_image
                )
                response["denture_images"].append(
                    {
                        "image_url": cloudinary_response["url"],
                        "confidence": [
                            f"{conf:.2f}"
                            for *box, conf, cls in results.pred[0].tolist()
                        ],
                    }
                )

            return Response(response, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
