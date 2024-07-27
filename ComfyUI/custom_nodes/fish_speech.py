
import torch
from pathlib import Path


from comfy.fish_speech.llama_utils import load_model as load_llama_model
from comfy.fish_speech.vqgan_utils import load_model as load_vqgan_model
from comfy.fish_speech.vqgan_utils import audio2prompt, semantic2audio
from comfy.fish_speech.llama_utils import prompt2semantic


CKPTS_FOLDER =  (Path("ComfyUI") / "models" / "fish_speech" / "checkpoints")
CONFIGS_FOLDER = (Path("ComfyUI") / "models" / "fish_speech" / "configs")

class LoadVQGAN:
    def __init__(self):
        self.vqgan = None
        pass
    
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "config": ([str(c.relative_to(CONFIGS_FOLDER)) for c in CONFIGS_FOLDER.glob("*vq*.yaml")], {"default": "firefly_gan_vq.yaml"}),
                "model": ([str(p.relative_to(CKPTS_FOLDER)) for p in CKPTS_FOLDER.glob("**/*vq*.pth")], ), 
                "device": (["cuda", "cpu"], {"default": "cuda"}),
            },
        }
    
    @classmethod
    def IS_CHANGED(s, model):
        return ""

    @classmethod
    def VALIDATE_INPUTS(s, model):
        return True

    RETURN_TYPES = ("VQGAN", )
    RETURN_NAMES = ("vqgan", )

    FUNCTION = "load_vqgan"

    #OUTPUT_NODE = False

    CATEGORY = "fishaudio/loaders"

    def load_vqgan(self, config, model, device):
        config = config.rsplit(".", 1)[0]
        model = str(CKPTS_FOLDER / model)
        if self.vqgan is None:
            self.vqgan = load_vqgan_model(config, model, device=device)
        return (self.vqgan, )



class LoadLLAMA:
    def __init__(self):
        self.llama = None
        self.decode_func = None
        pass
    
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "model": ([str(p.relative_to(CKPTS_FOLDER)) for p in CKPTS_FOLDER.glob("*/")], {"default": "fish-speech-1.2-sft"}),
                "device": (["cuda", "cpu"], {"default": "cuda"}),
                "precision": (["bf16", "half"], {"default": "bf16"}),
                "compile": (["yes", "no"], {"default": "no"}),
            },
        }

    @classmethod
    def IS_CHANGED(s, model):
        return ""

    @classmethod
    def VALIDATE_INPUTS(s, model):
        return True

    RETURN_TYPES = ("LLAMA", "DECODE_FUNC",)
    RETURN_NAMES = ("llama", "decode_func",)

    FUNCTION = "load_llama"

    #OUTPUT_NODE = False

    CATEGORY = "fishaudio/loaders"

    def load_llama(self, model, device, precision, compile):
        model = str((CKPTS_FOLDER / model).resolve())
        precision = torch.bfloat16 if precision == "bf16" else torch.half
        compile=True if compile == "yes" else False
        if self.llama is None or self.decode_func is None:
            self.llama, self.decode_func = load_llama_model(model, device, precision, compile)
        return (self.llama, self.decode_func, )


class AudioToPrompt:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "vqgan": ("VQGAN", ),
                "audio": ("AUDIO", ),
                "device": (["cuda", "cpu"], {"default": "cuda"}),
            },
        }

    
    RETURN_TYPES = ("AUDIO", "NUMPY")
    RETURN_NAMES = ("restored_audio", "prompt_tokens")

    FUNCTION = "encode"

    #OUTPUT_NODE = False

    CATEGORY = "fishaudio/infer"

    def encode(self, vqgan, audio, device):
        return audio2prompt(vqgan, audio, device)
    


class Prompt2Semantic:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "llama": ("LLAMA", ),
                "decode_func": ("DECODE_FUNC", ),
                "device": (["cuda", "cpu"], {"default": "cuda"}),
                "text": ("STRING", {"multiline": True}),
                "prompt_text": ("STRING", {"multiline": True}),
                "prompt_tokens": ("NUMPY", ),
                "max_new_tokens": ("INT", {
                    "default": 1024, 
                    "min": 0,
                    "max": 2048,
                    "step": 8,
                    "display": "number",
                }),
                "top_p": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.6,
                    "max": 0.9,
                    "step": 0.01,
                    "display": "number",
                }),
                "repetition_penalty": ("FLOAT", {
                    "default": 1.2,
                    "min": 1.0,
                    "max": 1.5,
                    "step": 0.01,
                    "display": "number",
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.6,
                    "max": 0.9,
                    "step": 0.01,
                    "display": "number",
                }),
                "compile": (["yes", "no"], {"default": "no"}),
                "seed": ("INT", {
                    "default": 42,
                    "min": 0,
                    "max": 4294967295,
                    "step": 1,
                    "display": "number",
                }),
                "iterative_prompt": (["yes", "no"], {"default": "yes"}),
                "chunk_length": ("INT", {
                    "default": 100,
                    "min": 0,
                    "max": 500,
                    "step": 8,
                    "display": "number",
                }),
            },
        }
    
    RETURN_TYPES = ("NUMPY", )
    RETURN_NAMES = ("codes", )

    FUNCTION = "decode"

    #OUTPUT_NODE = False

    CATEGORY = "fishaudio/infer"

    def decode(
        self,
        llama,
        decode_func,
        device: str,
        text: str,
        prompt_text: str,
        prompt_tokens,
        max_new_tokens: int,
        top_p: int,
        repetition_penalty: float,
        temperature: float,
        compile: str,
        seed: int,
        iterative_prompt: str,
        chunk_length: int,
    ):
        print(
            device,
            text,
            prompt_text,
            max_new_tokens,
            top_p,
            repetition_penalty,
            temperature,
            compile,
            seed,
            iterative_prompt,
            chunk_length,
        )
        return prompt2semantic(
            llama,
            decode_func,
            text,
            [prompt_text,],
            [prompt_tokens,],
            max_new_tokens,
            top_p,
            repetition_penalty,
            temperature,
            device,
            compile=True if compile == "yes" else False,
            seed=seed,
            iterative_prompt=True if iterative_prompt == "yes" else False,
            chunk_length=chunk_length,
        )



class Semantic2Audio:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "vqgan": ("VQGAN", ),
                "codes": ("NUMPY", ),
                "device": (["cuda", "cpu"], {"default": "cuda"}),
            },
        }

    RETURN_TYPES = ("AUDIO", )
    RETURN_NAMES = ("generated_audio", )

    FUNCTION = "generate"

    #OUTPUT_NODE = False

    CATEGORY = "fishaudio/infer"

    def generate(self, vqgan, codes, device):
        return semantic2audio(vqgan, codes, device)



NODE_CLASS_MAPPINGS = {
    "LoadVQGAN": LoadVQGAN,
    "LoadLLAMA": LoadLLAMA,
    "AudioToPrompt": AudioToPrompt,
    "Prompt2Semantic": Prompt2Semantic,
    "Semantic2Audio": Semantic2Audio,
}


# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadVQGAN": "LoadVQGAN",
    "LoadLLAMA": "LoadLLAMA",
    "AudioToPrompt": "AudioToPrompt",
    "Prompt2Semantic": "Prompt2Semantic",
    "Semantic2Audio": "Semantic2Audio",
}

