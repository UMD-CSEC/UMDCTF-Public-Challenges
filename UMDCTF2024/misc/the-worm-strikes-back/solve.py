import torch
from torch.autograd import Variable
import torchvision
from torchvision import models
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.utils.data.sampler import SubsetRandomSampler

import numpy as np
import os
from PIL import Image

def dataloader(train_size, test_size, data_dir, num_workers):
    train_transforms = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor()
    ])

    test_transforms = transforms.Compose([
        transforms.Resize(size=(224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor()
    ])

    index = np.arange(len(os.listdir(data_dir+"/worms")))
    np.random.shuffle(index)
    train_index = index[:train_size]
    test_index = index[train_size: (train_size + test_size)]

    train_dataset = torchvision.datasets.ImageFolder(root=data_dir, transform=train_transforms)
    test_dataset = torchvision.datasets.ImageFolder(root=data_dir, transform=test_transforms)

    train_loader = DataLoader(dataset=train_dataset, batch_size=1, sampler=SubsetRandomSampler(train_index), num_workers=num_workers, pin_memory=True, shuffle=False)
    test_loader = DataLoader(dataset=test_dataset, batch_size=1, sampler=SubsetRandomSampler(test_index), num_workers=num_workers, pin_memory=True, shuffle=False)
    return train_loader, test_loader

def mask_generation(patch=None, image_size=(3, 224, 224)):
    applied_patch = np.zeros(image_size)

    rotation_angle = np.random.choice(4)
    for i in range(patch.shape[0]):
        patch[i] = np.rot90(patch[i], rotation_angle)

    x_location, y_location = np.random.randint(low=0, high=image_size[1]-patch.shape[1]), np.random.randint(low=0, high=image_size[2]-patch.shape[2])
    applied_patch[:, x_location:x_location + patch.shape[1], y_location:y_location + patch.shape[2]] = patch
    mask = applied_patch.copy()
    mask[mask != 0] = 1.0
    return applied_patch, mask, x_location, y_location

def test_patch(patch, test_loader, model):
    model.eval()
    test_total, test_success = 0, 0
    for (image, _) in test_loader:
        test_total += 1
        applied_patch, mask, _, _ = mask_generation(patch, image_size=(3, 224, 224))
        applied_patch = torch.from_numpy(applied_patch)
        mask = torch.from_numpy(mask)
        perturbated_image = torch.mul(mask.type(torch.FloatTensor), applied_patch.type(torch.FloatTensor)) + torch.mul((1 - mask.type(torch.FloatTensor)), image.type(torch.FloatTensor))
        output = model(perturbated_image)
        predicted = (output > 0).int()
        if predicted == 0:
            test_success += 1
    return test_success / test_total

def patch_attack(image, applied_patch, mask, probability_threshold, model, lr=1, max_iteration=100):
    model.eval()
    applied_patch = torch.from_numpy(applied_patch)
    mask = torch.from_numpy(mask)
    target_probability, count = 0, 0
    perturbated_image = torch.mul(mask.type(torch.FloatTensor), applied_patch.type(torch.FloatTensor)) + torch.mul((1 - mask.type(torch.FloatTensor)), image.type(torch.FloatTensor))
    while target_probability < probability_threshold and count < max_iteration:
        count += 1

        perturbated_image = Variable(perturbated_image.data, requires_grad=True)
        per_image = perturbated_image
        output = model(per_image)
        target_log_sigmoid = torch.nn.functional.logsigmoid(-output)
        target_log_sigmoid.backward()
        patch_grad = perturbated_image.grad.clone()
        perturbated_image.grad.data.zero_()
        applied_patch = lr * patch_grad + applied_patch.type(torch.FloatTensor)
        applied_patch = torch.clamp(applied_patch, min=0, max=1)

        perturbated_image = torch.mul(mask.type(torch.FloatTensor), applied_patch.type(torch.FloatTensor)) + torch.mul((1-mask.type(torch.FloatTensor)), image.type(torch.FloatTensor))
        perturbated_image = torch.clamp(perturbated_image, min=0, max=1)
        output = model(perturbated_image)
        target_probability = 1 - torch.sigmoid(output).item()
    perturbated_image = perturbated_image.numpy()
    applied_patch = applied_patch.numpy()
    return perturbated_image, applied_patch

model = models.resnet18()
model.fc = torch.nn.Linear(model.fc.in_features, 1)
model.load_state_dict(torch.load("model.pt"))
model.eval()

train_loader, test_loader = dataloader(60, 18, "./data", 4)

patch = np.random.rand(3, 40, 40)

best_patch_epoch, best_patch_success_rate = 0, 0

for epoch in range(20):
    train_total, train_success = 0, 0
    for (image, _) in train_loader:
        train_total += 1
        applied_patch, mask, x_location, y_location = mask_generation(patch, image_size=(3, 224, 224))
        perturbated_image, applied_patch = patch_attack(image, applied_patch, mask, 0.9, model)
        perturbated_image = torch.from_numpy(perturbated_image)
        output = model(perturbated_image)
        predicted = (output > 0).int()
        if predicted == 0:
            train_success += 1
        patch = applied_patch[0][:, x_location:x_location + patch.shape[1], y_location:y_location + patch.shape[2]]
    Image.fromarray((np.clip(np.transpose(patch, (1, 2, 0)), 0, 1) * 255).astype(np.uint8)).save("out/patch_" + str(epoch) + ".png")
    print("Epoch:{} Patch attack success rate on trainset: {:.3f}%".format(epoch, 100 * train_success / train_total))
    train_success_rate = test_patch(patch, train_loader, model)
    print("Epoch:{} Patch attack success rate on trainset: {:.3f}%".format(epoch, 100 * train_success_rate))
    test_success_rate = test_patch(patch, test_loader, model)
    print("Epoch:{} Patch attack success rate on testset: {:.3f}%".format(epoch, 100 * test_success_rate))

    if test_success_rate > best_patch_success_rate:
        best_patch_success_rate = test_success_rate
        best_patch_epoch = epoch
        Image.fromarray((np.clip(np.transpose(patch, (1, 2, 0)), 0, 1) * 255).astype(np.uint8)).save("out/patch_best.png")

print("The best patch is found at epoch {} with success rate {}% on testset".format(best_patch_epoch, 100 * best_patch_success_rate))