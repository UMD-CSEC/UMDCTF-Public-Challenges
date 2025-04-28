import torch
import torch.nn as nn
import torchvision
from torchvision import datasets, transforms

def train_model(model, criterion, optimizer, scheduler, num_epochs=25):
    for epoch in range(num_epochs):
        print(f"Epoch {epoch}/{num_epochs - 1}")
        print("-" * 10)
        model.train()

        running_loss = 0.0
        running_corrects = 0

        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device).unsqueeze(1).float()

            optimizer.zero_grad()

            with torch.set_grad_enabled(True):
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                preds = (outputs > 0.0).float()
                loss.backward()
                optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)

        scheduler.step()

        epoch_loss = running_loss / dataset_size
        epoch_acc = running_corrects.double() / dataset_size

        print(f"Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

    return model


data_transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)

data_dir = "dataset"
image_dataset = datasets.ImageFolder(root=data_dir, transform=data_transform)
dataloader = torch.utils.data.DataLoader(
    image_dataset, batch_size=64, shuffle=True, num_workers=4
)
dataset_size = len(image_dataset)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = torchvision.models.resnet18(weights="IMAGENET1K_V1")
for param in model.parameters():
    param.requires_grad = False
model.fc = nn.Linear(model.fc.in_features, 1)

model = model.to(device)

criterion = nn.BCEWithLogitsLoss()

optimizer = torch.optim.SGD(model.parameters(), lr=0.001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.5)

model.load_state_dict(torch.load("model.pt"))
model = train_model(model, criterion, optimizer, scheduler, num_epochs=50)
torch.save(model.state_dict(), "model.pt")