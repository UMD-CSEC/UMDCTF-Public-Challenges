import random

import numpy as np
import torch
from diffusers import AutoencoderKL, DDIMScheduler, UNet2DConditionModel
from PIL import Image
from tqdm.auto import tqdm
from transformers import CLIPTextModel, CLIPTokenizer

model_path_clip = "openai/clip-vit-large-patch14"
clip_tokenizer = CLIPTokenizer.from_pretrained(model_path_clip)
clip = CLIPTextModel.from_pretrained(model_path_clip, torch_dtype=torch.float32)

with open("../hf_auth", "r") as f:
    auth_token = f.readlines()[0].strip()

model_path_diffusion = "CompVis/stable-diffusion-v1-4"
unet = UNet2DConditionModel.from_pretrained(
    model_path_diffusion,
    subfolder="unet",
    use_auth_token=auth_token,
    variant="fp16",
    torch_dtype=torch.float32,
)
vae = AutoencoderKL.from_pretrained(
    model_path_diffusion,
    subfolder="vae",
    use_auth_token=auth_token,
    variant="fp16",
    torch_dtype=torch.float32,
)

def tensor_to_image(tensor):
    image = (tensor / 2 + 0.5).clamp(0, 1)
    image = image.permute(0, 2, 3, 1).numpy()
    image = (image[0] * 255).round().astype("uint8")
    return Image.fromarray(image)

def image_to_np(image):
    return np.array(image).astype(np.float32) / 255.0 * 2.0 - 1.0

def interp_prev_alpha(prev_t, scheduler):
    if prev_t < 0:
        return scheduler.final_alpha_cumprod

    low = prev_t.floor().long()
    high = prev_t.ceil().long()
    rem = prev_t - low

    low_alpha = scheduler.alphas_cumprod[low]
    high_alpha = scheduler.alphas_cumprod[high]
    return low_alpha * rem + high_alpha * (1 - rem)


@torch.no_grad()
def invert_stablediffusion(
    image,
    prompt="",
    guidance_scale=7.0,
    steps=50,
):
    seed = random.randrange(2**32 - 1)
    generator = torch.manual_seed(seed)

    image = image_to_np(image)
    image = torch.from_numpy(image[np.newaxis, ...].transpose(0, 3, 1, 2))
    latent = (
        vae.encode(image).latent_dist.sample(generator=generator) * 0.18215
    )

    scheduler = DDIMScheduler(
        beta_start=0.00085,
        beta_end=0.012,
        beta_schedule="scaled_linear",
        num_train_timesteps=1000,
        clip_sample=False,
        set_alpha_to_one=False,
    )
    scheduler.set_timesteps(steps)

    tokens_unconditional = clip_tokenizer(
        "",
        padding="max_length",
        max_length=clip_tokenizer.model_max_length,
        truncation=True,
        return_tensors="pt",
        return_overflowing_tokens=True,
    )
    embedding_unconditional = clip(tokens_unconditional.input_ids).last_hidden_state

    tokens_conditional = clip_tokenizer(
        prompt,
        padding="max_length",
        max_length=clip_tokenizer.model_max_length,
        truncation=True,
        return_tensors="pt",
        return_overflowing_tokens=True,
    )
    embedding_conditional = clip(tokens_conditional.input_ids).last_hidden_state

    timesteps = scheduler.timesteps.flip(0)
    for t in tqdm(timesteps):
        noise_pred_uncond = unet(
            latent, t, encoder_hidden_states=embedding_unconditional
        ).sample

        noise_pred_cond = unet(
            latent, t, encoder_hidden_states=embedding_conditional
        ).sample

        grad = noise_pred_cond - noise_pred_uncond
        noise_pred = noise_pred_uncond + guidance_scale * grad

        prev_t = (
            t - scheduler.config.num_train_timesteps / scheduler.num_inference_steps
        )
        alpha_prod_t = scheduler.alphas_cumprod[t]
        beta_prod_t = 1 - alpha_prod_t

        alpha_prod_t_prev = interp_prev_alpha(prev_t, scheduler)

        alpha_quotient = (alpha_prod_t / alpha_prod_t_prev) ** 0.5
        first_term = alpha_quotient * latent
        second_term = ((beta_prod_t) ** 0.5) * noise_pred
        third_term = alpha_quotient * ((1 - alpha_prod_t_prev) ** 0.5) * noise_pred
        latent = first_term + second_term - third_term

    return latent

tralalero_tralala = Image.open("../tralalero_tralala.jpg")
latent = invert_stablediffusion(tralalero_tralala)
rands = latent.flatten()
for i in range(0, rands.numel() - 15, 16):
    for j in range(8):
        x = rands[i + j]
        y = rands[i + j + 8]
        u = 1 - torch.exp((x**2 + y**2) / -2)
        v = ((torch.atan2(y, x) + 2 * torch.pi) % (2 * torch.pi)) / (2 * torch.pi)
        u *= 16777216.0
        v *= 16777216.0
        rands[i + j] = u
        rands[i + j + 8] = v
rands = list(map(int, list(rands.round())))
with open("./rands.txt", "w") as f:
    f.write("\n".join(map(str, rands)))