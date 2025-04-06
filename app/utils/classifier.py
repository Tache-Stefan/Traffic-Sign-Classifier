import torch
from train import load_model
from app.utils import config


def predict_image(image_path):
    from PIL import Image
    net = load_model()

    image = Image.open(image_path).convert("RGB")
    image = config.transform(image).unsqueeze(0).to(config.device)

    with torch.no_grad():
        output = net(image)
        _, predicted_class = torch.max(output, 1)

    return predicted_class.item()