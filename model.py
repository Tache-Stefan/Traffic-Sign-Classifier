import torch.nn as nn
import torch.optim as optim
from app.utils import config
from torchvision.models import resnet18, ResNet18_Weights


class TrafficSignCNN(nn.Module):
    def __init__(self, num_classes = config.NUM_CLASSES):
        super(TrafficSignCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.bn1 = nn.BatchNorm2d(32)
        self.bn2 = nn.BatchNorm2d(64)
        self.bn3 = nn.BatchNorm2d(128)
        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(128 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = self.pool(self.relu(self.bn3(self.conv3(x))))
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


def get_model(model_name='CNN'):
    num_classes = 43

    if model_name == 'ResNet18':
        model = resnet18(weights=ResNet18_Weights.DEFAULT)

        for param in model.parameters():
            param.requires_grad = False
        for name, param in model.named_parameters():
            if "layer4" in name or "fc" in name:
                param.requires_grad = True

        model.fc = nn.Sequential(
            nn.Linear(model.fc.in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

        return model.to(config.device)

    elif model_name == 'CNN':
        model = TrafficSignCNN()
        return model.to(config.device)

    raise ValueError("Unsupported model: {}".format(model_name))


def get_optimizer(model):
    return optim.Adam(model.parameters(), lr=0.001)


def get_criterion():
    return nn.CrossEntropyLoss()
