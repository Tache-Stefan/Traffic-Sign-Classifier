import os
from PIL import Image
from torch.utils.data import Dataset
from app.utils import config


class TrafficSignDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = []
        self.labels = []

        for class_id in range(config.NUM_CLASSES):
            class_path = os.path.join(root_dir, f"{class_id:05d}")
            for img_name in os.listdir(class_path):
                img_path = os.path.join(class_path, img_name)
                if img_name.endswith('.ppm'):
                    self.images.append(img_path)
                    self.labels.append(class_id)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]
        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, label
