import cv2
import torch
import diffusers
from src.state import state
from src.logger import log


torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction = True
torch.backends.cuda.matmul.allow_bf16_reduced_precision_reduction = True
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.allow_tf32 = True


pipe = None
load_config = {
    "low_cpu_mem_usage": True,
    "torch_dtype": torch.float16 if state.dtype == 'fp16' else torch.float32,
    "safety_checker": None,
    "requires_safety_checker": False,
    "use_safetensors": True,
    "cache_dir": "models",
    "variant": "fp16" if state.dtype == 'fp16' else None,
    "load_connected_pipeline": True,
    "custom_pipeline": "latent_consistency_img2img"
}


def model(image):
    global pipe # pylint: disable=global-statement
    if pipe is None:
        pipe = diffusers.DiffusionPipeline.from_pretrained(state.model, **load_config)
        pipe = pipe.to(state.device)
        log(f'model loading: file={state.model} config={load_config}')
        # pipe = diffusers.AutoPipelineForText2Image.from_pretrained(state.model, **load_config)
        # pipe = diffusers.AutoPipelineForImage2Image.from_pipe(pipe)
        log(f'model loaded: file={state.model}')
        state.loaded = True

    # prompt_embeds, _ = pipe.encode_prompt(prompt=state.prompt, device=state.device, num_images_per_prompt=1, False, negative_prompt=None, prompt_embeds=prompt_embeds, negative_prompt_embeds=None, lora_scale=1, clip_skip=1) # TODO embeds
    # with torch.no_grad(), torch.autocast(state.device):
    image = cv2.resize(image, dsize=(int(image.shape[1] * state.scale), int(image.shape[0] * state.scale)))
    image = image / 127.5 - 1.0
    output = pipe(
        prompt=state.prompt,
        num_inference_steps=state.steps,
        image=image, # already np.array from cv2
        strength=state.strength,
        # generator=torch.Generator(state.device).manual_seed(state.seed), # TODO pipeline mismatch with custom_pipeline
        output_type='pil') # TODO latent
    return output.images[0]
