import random
import sys

import numpy as np
import torch
from diffusers import AutoencoderKL, DDIMScheduler, UNet2DConditionModel
from PIL import Image
from tqdm.auto import tqdm
from transformers import CLIPTextModel, CLIPTokenizer

def load():
    model_path_clip = "openai/clip-vit-large-patch14"
    clip_tokenizer = CLIPTokenizer.from_pretrained(model_path_clip)
    clip = CLIPTextModel.from_pretrained(model_path_clip, torch_dtype=torch.float32)

    with open("hf_auth", "r") as f:
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
    return (clip_tokenizer, clip, unet, vae)

def run(models, state_bytes):
    (clip_tokenizer, clip, unet, vae) = models

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
    def stablediffusion(
        prompt="",
        guidance_scale=7.0,
        steps=50,
        state=None,
        width=96,
        height=96,
    ):
        seed = random.randrange(2**32 - 1)
        generator = torch.manual_seed(seed)
        if state is not None:
            generator.set_state(state)

        latent = torch.randn(
            (1, unet.config.in_channels, height // 8, width // 8),
            generator=generator,
            dtype=torch.float32,
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

        for t in tqdm(scheduler.timesteps):
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
            first_term = (1.0 / alpha_quotient) * latent
            second_term = (1.0 / alpha_quotient) * (beta_prod_t**0.5) * noise_pred
            third_term = ((1 - alpha_prod_t_prev) ** 0.5) * noise_pred
            latent = first_term - second_term + third_term

        image = vae.decode(latent / 0.18215).sample
        return tensor_to_image(image)

    try:
        state = torch.ByteTensor(state_bytes)
        generated_image = stablediffusion(state=state)
    except Exception as e:
        return str(e)

    generated_np = image_to_np(generated_image)

    tralalero_tralala = Image.open("tralalero_tralala.jpg")
    tralalero_tralala_np = image_to_np(tralalero_tralala)

    mse = np.square(tralalero_tralala_np - generated_np).mean()

    if mse > 0.05:
        return "sorry bud im not seeing tralalero tralala"

    with open("flag.txt", "r") as f:
        return f.read()
