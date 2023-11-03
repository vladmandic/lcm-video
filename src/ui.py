import time
import gradio as gr
from src.logger import log
from src.state import state
import src.media as media
import src.process as process


output = None
css = """
    :root .dark {
        --background-fill-primary: black; --block-background-fill: black; --border-color-primary: black; --body-text-color: #CCC; --block-padding: 0; --spacing-lg: 0;
    }
    .gradio-container { max-width: unset !important; }
    .tab-nav { background: var(--input-background-fill) }
    .tab-nav .selected { background: var(--button-secondary-background-fill) }
    .generating { animation: unset !important; border: none !important; }
    .prose { font-family: monospace; font-size: 0.8em !important; color: #aaa !important; line-height: 1.4em; }
    footer { display: none !important; }
    button { max-width: 2em; max-height: 2em; padding: 0 !important; }
"""

def start(upload_btn):
    global output # pylint: disable=global-statement # keeping global so previous frame results can be buffered
    if upload_btn is not None:
        if state.input != upload_btn.name:
            state.stream = None # reinit stream on media change
        state.input = upload_btn.name

    state.started = True
    state.n = 0
    frame = media.video()
    html = log(f'start: {state.__dict__}') if frame is not None else log('error: video start failed')
    yield None, None, html
    while state.started:
        t0 = time.time()
        frame = media.video()
        state.n += 1
        if frame is None:
            state.started = False
            break
        if state.skip == 0 or state.n % state.skip == 0:
            output = process.model(frame)
            t1 = time.time()
            if state.n % 10 == 0:
                html = log(f'frame={state.n} time={t1-t0:.2f} fps={1/(t1-t0):.2f}')
        yield frame, output, html


def stop():
    state.started = False
    state.stream = None
    html = log('stop')
    return html


def main():
    log('app starting')

    def change(taesd_cb, scale_num, steps_num, strength_num, skip_num, prompt_txt, webcam_btn, upload_btn):
        state.taesd = taesd_cb
        state.scale = scale_num
        state.steps = steps_num
        state.skip = skip_num
        state.strength = strength_num
        state.prompt = prompt_txt
        state.webcam = webcam_btn # TODO webcam
        if upload_btn is not None:
            if state.input != upload_btn.name:
                state.stream = None # reinit stream on media change
            state.input = upload_btn.name
        html = log(f'config: {state.__dict__}')
        return html

    with gr.Blocks(css=css, title='LCM Video') as app:
        with gr.Row():
            with gr.Column():
                input_img = gr.Image(label='Input', show_label=False, interactive=False, height=512)
            with gr.Column():
                output_img = gr.Image(label='output', show_label=False, interactive=False, height=512)
        with gr.Row():
            taesd_cb = gr.Checkbox(label='Quick', value=True)
            steps_num = gr.Slider(label='Steps', value=state.steps, minimum=1, maximum=20, step=1)
            strength_num = gr.Slider(label='Strength', value=state.strength, minimum=0.1, maximum=1.0, step=0.05)
            skip_num = gr.Slider(label='Skip', value=state.skip, minimum=0, maximum=20, step=1)
            scale_num = gr.Slider(label='Scale', value=state.scale, minimum=0.1, maximum=2.0, step=0.1)
        with gr.Row():
            prompt_txt = gr.Text(label='Prompt', default='')
        with gr.Row():
            webcam_btn = gr.Button(value="WebCam")
            upload_btn = gr.UploadButton(label="Video", file_types=['video'])
            start_btn = gr.Button(value="Start")
            stop_btn = gr.Button(value="Stop")
        with gr.Row():
            log_html = gr.HTML('')
            start_btn.click(fn=start, inputs=[upload_btn], outputs=[input_img, output_img, log_html], show_progress=False)
            stop_btn.click(fn=stop, inputs=[], outputs=[log_html])
        taesd_cb.change(fn=change, inputs=[taesd_cb, scale_num, steps_num, strength_num, skip_num, prompt_txt, webcam_btn, upload_btn], outputs=[log_html])
        scale_num.change(fn=change, inputs=[taesd_cb, scale_num, steps_num, strength_num, skip_num, prompt_txt, webcam_btn, upload_btn], outputs=[log_html])
        steps_num.change(fn=change, inputs=[taesd_cb, scale_num, steps_num, strength_num, skip_num, prompt_txt, webcam_btn, upload_btn], outputs=[log_html])
        skip_num.change(fn=change, inputs=[taesd_cb, scale_num, steps_num, strength_num, skip_num, prompt_txt, webcam_btn, upload_btn], outputs=[log_html])
        strength_num.change(fn=change, inputs=[taesd_cb, scale_num, steps_num, strength_num, skip_num, prompt_txt, webcam_btn, upload_btn], outputs=[log_html])
        prompt_txt.change(fn=change, inputs=[taesd_cb, scale_num, steps_num, strength_num, skip_num, prompt_txt, webcam_btn, upload_btn], outputs=[log_html])
        webcam_btn.click(fn=change, inputs=[taesd_cb, scale_num, steps_num, strength_num, skip_num, prompt_txt, webcam_btn, upload_btn], outputs=[log_html])
    app.queue(concurrency_count=4, max_size=16).launch()
