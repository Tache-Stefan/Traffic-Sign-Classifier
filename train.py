import torch
from torch.utils.data import DataLoader
from dataset import TrafficSignDataset
import model
import config


def train_model():
    dataset = TrafficSignDataset(config.DATASET_PATH, transform=config.transform)

    train_size = int(0.75 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=config.BATCH_SIZE, shuffle=False)

    net = model.get_model().to(config.device)
    criterion = model.get_criterion()
    optimizer = model.get_optimizer(net)

    for epoch in range(config.EPOCHS):
        net.train()
        running_loss = 0.0

        for images, labels in train_loader:
            images, labels = images.to(config.device), labels.to(config.device)

            optimizer.zero_grad()
            outputs = net(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            print(f"Epoch {epoch + 1}/{config.EPOCHS}, Loss: {running_loss / len(train_loader):.4f}")

    print("Training Complete")

    correct = 0
    total = 0
    net.eval()
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(config.device), labels.to(config.device)
            outputs = net(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print(f"Test Accuracy: {100 * correct / total:.2f}%")

    torch.save(net.state_dict(), "model.pth")


def load_model(model_path='model.pth'):
    net = model.get_model().to(config.device)
    net.load_state_dict(torch.load(model_path))
    net.eval()
    return net


def predict_image(image_path):
    from PIL import Image
    net = load_model()

    image = Image.open(image_path).convert("RGB")
    image = config.transform(image).unsqueeze(0).to(config.device)

    with torch.no_grad():
        output = net(image)
        _, predicted_class = torch.max(output, 1)

    return predicted_class.item()


if __name__ == "__main__":
    train_model()
