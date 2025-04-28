# method based on https://arxiv.org/abs/2402.01879

import math

import torch
from torch import nn

from torchvision.models import resnet18
import torchvision.transforms as T

from PIL import Image

# load model
model = resnet18()
model.fc = nn.Linear(model.fc.in_features, 1)
model.load_state_dict(torch.load("model.pt"))

# load worm
worm = Image.open("worm.png")
worm = T.ToTensor()(worm).unsqueeze(0)
int_worm = (worm * 255).int()

# initialize perturbation
d = torch.zeros_like(worm, requires_grad=True)

# define number of optimization steps
num_steps = 25000

# define loss function and optimizer
criterion = nn.BCEWithLogitsLoss()
optim = torch.optim.Adam([d], lr=1.0)

# initialize best adversarial perturbation
best_adv_l0 = worm[0, 0].numel()
best_adv = worm.clone()

# initialize sparsity threshold
t = torch.tensor(0.3)

# perform optimization
for i in range(num_steps):
    # compute adversarial image
    adv_worm = worm + d

    # compute classification loss
    logits = model(adv_worm)
    bce_loss = criterion(logits, torch.tensor([[1.]]))

    # save best adversarial perturbation
    is_adv = (logits < 0).squeeze()
    new_l0 = torch.count_nonzero(((adv_worm * 255).int() - int_worm).abs().sum(dim=1)).item()
    if is_adv and new_l0 < best_adv_l0:
        best_adv_l0 = new_l0
        best_adv = adv_worm.detach().clone()

    # compute full loss including L_0 norm approximation
    # I also tried the below commented pixelwise L_0 approximation,
    # but it didn't work as well despite being what I'm really trying to obtain
    # l0_approx_normalized = (d.square() / (d.square() + 0.001)).sum(dim=1).clamp(0, 1).mean()
    l0_approx_normalized = (d.square() / (d.square() + 0.001)).mean()
    adv_loss = (-bce_loss + l0_approx_normalized)

    # compute gradient
    optim.zero_grad()
    adv_loss.backward()

    # normalize gradient with respect to L_inf norm
    d_grad_inf_norm = d.grad.norm(p=float("inf")).clamp_(min=1e-12)
    d.grad.div_(d_grad_inf_norm)

    # update perturbation
    optim.step()

    # clamp perturbation such that the resulting image is between 0 and 1
    d.data.add_(worm).clamp_(0, 1).sub_(worm)

    # adjust learning rate according to cosine annealing schedule
    n = 0.1 + 0.9 * (1 + math.cos(math.pi * i / num_steps)) / 2
    optim.param_groups[0]['lr'] = n

    # adjust sparsity threshold
    # if the adversarial image is misclassified, increase the threshold to encourage sparsity
    # if the adversarial image is classified correctly, decrease the threshold to encourage misclassification
    t.add_(torch.where(is_adv, 0.01 * n, -0.01 * n)).clamp_(0, 1)

    # filter components by sparsity threshold
    d.data[d.data.abs() < t] = 0

# define pixel tensors for original image and adversarial image
out = (best_adv * 255).int().squeeze().transpose(0, 1).transpose(1, 2)
worm = int_worm.squeeze().transpose(0, 1).transpose(1, 2)

# save adversarial image so we can look at it
Image.fromarray(out.numpy().astype("uint8")).save("out.png")

# print the adversarial image in the format expected by the server
changed_px = torch.nonzero((out - worm).abs().sum(dim=2))
out_str = ";".join([f"{x},{y},{','.join(map(str, out[y, x].tolist()))}" for y, x in changed_px])
print(out_str)
print(len(changed_px))
