class State():
    steps: int = 5
    scale: float = 0.5
    dtype: str = 'fp16'
    cache_dir: str = '/mnt/f/Models/Diffusers'
    model: str = 'SimianLuo/LCM_Dreamshaper_v7'
    device: str = 'cuda'
    strength: float = 0.4
    prompt: str = ''
    taesd: bool = True
    webcam: bool = False
    input: str = None
    stream = None
    loaded: bool = False
    started: bool = False
    n: int = 0
    skip: int = 0


state = State()
