import streamlit as st
from jina import Client, Executor, requests, DocumentArray, Document
import os
import asyncio
from random import randint
from yaml import Loader, load as load_yaml
import base64
from io import BytesIO
from PIL import Image, ImageDraw

st.set_page_config(page_title="Disco Diffusion UI", page_icon="🎨", layout="wide")
st.title('Disco Diffusion UI')
# form = st.form("prompt_form")
textinput_left, textinput_right = st.columns([10, 1])
left, center, right = st.columns([1, 3, 1])
[image_preview_tab, past_images_tab] = center.tabs(["Image Preview", "Past Images"])
# image_preview_tab_container = image_preview_tab.container()
no_prompt_text_container = image_preview_tab.empty()
no_prompt_text_container.warning("Nothing but crickets here, try generating something first.")

# ENV Variables
HOST_LOCATION = os.environ['SERVER_LOCATION']

DIFFUSION_MODELS = [*load_yaml(open('models.yml'), Loader=Loader)]
CLIP_MODELS = ['RN50::openai', 'RN50::yfcc15m', 'RN50::cc12m', 'RN50-quickgelu::openai', 'RN50-quickgelu::yfcc15m', 'RN50-quickgelu::cc12m', 'RN101::openai', 'RN101::yfcc15m', 'RN101-quickgelu::openai', 'RN101-quickgelu::yfcc15m', 'RN50x4::openai', 'RN50x16::openai', 'RN50x64::openai', 'ViT-B-32::openai', 'ViT-B-32::laion400m_e31', 'ViT-B-32::laion400m_e32', 'ViT-B-32::laion2b_e16', 'ViT-B-32::laion2b_s34b_b79k', 'ViT-B-32-quickgelu::openai', 'ViT-B-32-quickgelu::laion400m_e31', 'ViT-B-32-quickgelu::laion400m_e32', 'ViT-B-16::openai', 'ViT-B-16::laion400m_e31', 'ViT-B-16::laion400m_e32', 'ViT-B-16-plus-240::laion400m_e31', 'ViT-B-16-plus-240::laion400m_e32', 'ViT-L-14::openai', 'ViT-L-14::laion400m_e31', 'ViT-L-14::laion400m_e32', 'ViT-L-14::laion2b_s32b_b82k', 'ViT-L-14-336::openai', 'ViT-H-14::laion2b_s32b_b79k', 'ViT-g-14::laion2b_s12b_b42k'] # https://github.com/mlfoundations/open_clip#pretrained-model-interface

# Initialize session state
# st.session_state['create_request'] = []
st.session_state['name_docarray'] = "mydisco-" + str(randint(0, 1000))

st.session_state['create_task'] = None
st.session_state['preview_task'] = None

st.session_state['status'] = 'idle'

client = Client(host=HOST_LOCATION, asyncio=True)

create_response_array = []

# Default for session state advanced settings

STEPS_DEFAULT = 200
GIF_FPS_DEFAULT = 20
SAVE_RATE_DEFAULT = 20

CUT_IC_POW_DEFAULT = 1
CLAMP_MAX_DEFAULT = 0.05
CLIP_GUIDANCE_SCALE_DEFAULT = 5000
SKIP_STEPS_DEFAULT = 0
TV_SCALE_DEFAULT = 0
RANGE_SCALE_DEFAULT = 150
SAT_SCALE_DEFAULT = 0
CUTN_BATCHES_DEFAULT = 1
CUT_OVERVIEW_DEFAULT = "[12]*400+[4]*600"
CUT_INNERCUT_DEFAULT = "[4]*400+[12]*600"
CUT_ICGRAY_P_DEFAULT = "[0.2]*400+[0]*600"
ETA_DEFAULT = 0.8

INIT_SCALE_DEFAULT = 1000

async def disco_request(text_prompts: list, name_docarray: str):

    cut_ic_pow = st.session_state.get('cut_ic_pow', default = CUT_IC_POW_DEFAULT)
    clamp_max = st.session_state.get('clamp_max', default = CLAMP_MAX_DEFAULT)
    clip_guidance_scale = st.session_state.get('clip_guidance_scale', default = CLIP_GUIDANCE_SCALE_DEFAULT)
    skip_steps = st.session_state.get('skip_steps', default = SKIP_STEPS_DEFAULT)
    tv_scale = st.session_state.get('tv_scale', default = TV_SCALE_DEFAULT)
    range_scale = st.session_state.get('range_scale', default = RANGE_SCALE_DEFAULT)
    sat_scale = st.session_state.get('sat_scale', default = SAT_SCALE_DEFAULT)
    cutn_batches = st.session_state.get('cutn_batches', default = CUTN_BATCHES_DEFAULT)
    cut_overview = st.session_state.get('cut_overview', default = CUT_OVERVIEW_DEFAULT)
    cut_innercut = st.session_state.get('cut_innercut', default = CUT_INNERCUT_DEFAULT)
    cut_icgray_p = st.session_state.get('cut_icgray_p', default = CUT_ICGRAY_P_DEFAULT)
    eta = st.session_state.get('eta', default = ETA_DEFAULT)

    init_scale = st.session_state.get('init_scale', default = INIT_SCALE_DEFAULT)
    init_image = st.session_state.get('init_image', default = None)

    save_rate = st.session_state.get('save_rate', default = SAVE_RATE_DEFAULT)

    # clamp_max = st.session_state.clamp_max if ('clamp_max' not in st.session_state) else CLAMP_MAX_DEFAULT
    # clip_guidance_scale = st.session_state.clip_guidance_scale if ('clip_guidance_scale' not in st.session_state) else CLIP_GUIDANCE_SCALE_DEFAULT
    # skip_steps = st.session_state.skip_steps if ('skip_steps' not in st.session_state) else SKIP_STEPS_DEFAULT
    # tv_scale = st.session_state.tv_scale if ('tv_scale' not in st.session_state) else TV_SCALE_DEFAULT
    # range_scale = st.session_state.range_scale if ('range_scale' not in st.session_state) else RANGE_SCALE_DEFAULT
    # sat_scale = st.session_state.sat_scale if ('sat_scale' not in st.session_state) else SAT_SCALE_DEFAULT
    # cutn_batches = st.session_state.cutn_batches if ('cutn_batches' not in st.session_state) else CUTN_BATCHES_DEFAULT
    # cut_overview = st.session_state.cut_overview if ('cut_overview' not in st.session_state) else CUT_OVERVIEW_DEFAULT
    # cut_innercut = st.session_state.cut_innercut if ('cut_innercut' not in st.session_state) else CUT_INNERCUT_DEFAULT
    # cut_icgray_p = st.session_state.cut_icgray_p if ('cut_icgray_p' not in st.session_state) else CUT_ICGRAY_P_DEFAULT

    # setup parameters
    parameters = {
        'name_docarray': name_docarray,
        'text_prompts': text_prompts,
        'batch_size': 1,
        'cutn_batches': cutn_batches,
        'tv_scale': tv_scale,
        'range_scale': range_scale,
        'sat_scale': sat_scale,
        'n_batches': 1,
        'seed': st.session_state.seed,
        'steps': st.session_state.steps,
        'width_height': [st.session_state.width, st.session_state.height],
        'diffusion_model': st.session_state.diffusion_model,
        'clip_models': st.session_state.clip_models,
        'use_secondary_model': st.session_state.use_secondary_model,
        'clip_guidance_scale': clip_guidance_scale,
        'init_scale': init_scale,
        'cut_overview': cut_overview,
        'cut_innercut': cut_innercut,
        'cut_icgray_p': cut_icgray_p,
        'cut_ic_pow': cut_ic_pow,
        'clamp_max': clamp_max,
        'skip_steps': skip_steps,
        'save_rate': save_rate,
        'eta': eta,
    }

    # create the image
    if init_image:
        init_image_uri = 'data:image/png;base64,' + base64.b64encode(init_image.getvalue()).decode('utf-8')

        init_document = Document(
            mime_type='image/png',
            uri=init_image_uri,
        )
        print(init_document.summary())

        async for resp in client.post(
            '/create',
            init_document,
            parameters=parameters,
        ):
            create_response_array.append(resp)
    else:
        async for resp in client.post(
            '/create',
            parameters=parameters,
        ):
            create_response_array.append(resp)
    

    

# def blocking_disco_request(text_prompts: list, name_docarray: str):

#     blocking_client = Client(host=HOST_LOCATION)

#     blocking_client.post(
#         '/create',
#         parameters={
#             'name_docarray': name_docarray,
#             'text_prompts': text_prompts,
#             'batch_size': 1,
#             'cutn_batches': 1,
#             'n_batches': 1,
#             'steps': 10,
#             'width_height': [500, 500]
#         },
#     )

preview_response_array = []

async def preview_handler(name_docarray: str):

    # client = Client(host=HOST_LOCATION, asyncio=True)
    
    async for resp in client.post(
        '/result',
        parameters={
            'name_docarray': name_docarray
        },
    ):
        # await resp
        print("Run preview handler")
        # print(name_docarray)
        # print(resp)
        print(resp.summary())
        if len(resp) > 0:
            # print(resp[0])
            document = resp[0]
            print(document.summary())
            preview_response_array.append(document)
        # if resp.length > 0:
        #     print(resp[0])
        #     print(resp[0].summary())
    # await asyncio.sleep(1)

    

async def preview_handler_wait():
    # preview_task = asyncio.create_task(preview_handler(st.session_state.name_docarray))
    # print("Running the preview handler wait loop")
    completed = False
    no_prompt_text_container.empty()
    image_preview_tab.text("Progress: ")
    progress_bar = image_preview_tab.progress(0)
    preview_image = image_preview_tab.empty()
    while len(preview_response_array) < 1 or not completed:
        # print("Waiting for preview response")
        await asyncio.sleep(5)
        await preview_handler(st.session_state.name_docarray)
        # print("current length: " + str(len(preview_response_array)))
        # print("Waiting 1 second")
        # Add the image to preview
        if len(preview_response_array) > 0:
            latest_document = preview_response_array[-1]
            progress_bar.progress((st.session_state.get('skip_steps', default = SKIP_STEPS_DEFAULT) + latest_document.tags["_status"]["step"] + 1) / st.session_state.steps)
            preview_image.image(image=latest_document.uri)
            st.session_state["seed_record"] = str(int(latest_document.tags['seed']))
            completed = latest_document.tags["_status"]["completed"] is True
            st.session_state.status = 'completed'

def gif_generator(image_docarray: list()):
    progress_gif_slides = []
    for chunk_index, chunk in enumerate(image_docarray[-1].chunks):
        chunk.load_uri_to_blob()

        # Add ID to the image
        image = Image.open(BytesIO(chunk.content))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), str(chunk_index), (255, 255, 255))

        progress_gif_slides.append(image)
    
    # Convert images to gif
    progress_gif_iterator = iter(progress_gif_slides)
    progress_gif_iterator_first = next(progress_gif_iterator)

    progress_gif_buffer = BytesIO()
    
    progress_gif_iterator_first.save(
        fp=progress_gif_buffer,
        format='GIF',
        append_images=progress_gif_iterator,
        save_all=True,
        duration=(st.session_state.get('steps', default=STEPS_DEFAULT) * 8) // st.session_state.get('gif_fps', default=GIF_FPS_DEFAULT),
        loop=0,
    )
    progress_gif = 'data:image/gif;base64,' + base64.b64encode(progress_gif_buffer.getvalue()).decode('utf-8')
    return progress_gif 

async def prompt_handler():
    text_prompt_array = st.session_state.text_prompts.split(",")

    st.session_state.create_task = asyncio.create_task(disco_request(text_prompt_array, st.session_state.name_docarray))
    st.session_state.preview_task = asyncio.create_task(preview_handler_wait())
    # asyncio.to_thread(blocking_disco_request(st.session_state.text_prompts, st.session_state.name_docarray))
    
    st.session_state.status = 'running'

    await asyncio.gather(
        st.session_state.create_task,
        st.session_state.preview_task
    )

    # if len(preview_response_array) > 0:
    #     form.image(image=preview_response_array[0][0].uri)
    # else:
    if len(preview_response_array) < 1:
        image_preview_tab.write("Error")
        st.session_state.status = 'error'
    # await preview_handler_wait()

    # done
    # st.balloons()
    else:
        prompt_details = image_preview_tab.expander("Prompt Details", expanded=True)

        prompt_details.write("Prompt: " + st.session_state.text_prompts)
        prompt_details.write("Image ID: " + st.session_state.name_docarray)
        prompt_details.write("Seed: " + str(st.session_state.seed_record))
        prompt_details.write("Width: " + str(st.session_state.width))
        prompt_details.write("Height: " + str(st.session_state.height))
        prompt_details.write("Steps: " + str(st.session_state.steps))
        # prompt_details.write("Clip Guidance Scale: " + str(st.session_state.clip_guidance_scale))

        progress_gif_container = image_preview_tab.expander("Progress GIF", expanded=True)
        # create the gif
        # Create the images
        progress_gif = gif_generator(preview_response_array)

        progress_gif_container.image(progress_gif)




    # done, pending = await asyncio.wait({create_task})

    # while create_task in pending:
    #     print("Pending")
    #     await asyncio.sleep(1)

    # if create_task in done:
    #     print("Done once")
    
    # if create_task in pending:
    #     print("Pending once")

def click_handler():
    if st.session_state.get('text_prompts', default = '') == "":
        textinput_left.error("Please input a prompt")
        # text_input.help = "Please input a prompt"
        return
    if st.session_state.get('skip_steps', default = SKIP_STEPS_DEFAULT) > st.session_state.get('steps', default=STEPS_DEFAULT):
        textinput_left.error("Skip steps cannot be greater than steps")
        return
    
    asyncio.run(prompt_handler())

# def preview_click_handler(name_docarray):
#     a = dict(st.session_state)
#     print(st.session_state)
#     if name_docarray == "" or st.session_state.status == 'idle':
#         textinput_left.error("Please create a prompt first")
#     else:
#         st.session_state.name_docarray = name_docarray
#         if st.session_state.status == 'completed' or st.session_state.status == 'error':
#             st.session_state.preview_task = preview_handler_wait()
#             asyncio.run(st.session_state.preview_task)

async def past_image_click_retrieve(name_docarray):
    preview_image = past_images_tab.empty()
        
    await preview_handler(name_docarray)
    # print("current length: " + str(len(preview_response_array)))
    # print("Waiting 1 second")
    # Add the image to preview
    if len(preview_response_array) > 0:
        latest_document = preview_response_array[-1]
        preview_image.image(image=latest_document.uri)
    
        progress_gif_container = past_images_tab.expander("Progress GIF", expanded=True)

        progress_gif = gif_generator(preview_response_array)

        progress_gif_container.image(progress_gif)

def past_image_click_handler(name_docarray):
    asyncio.run(past_image_click_retrieve(name_docarray))

async def stop_prompt_handler(name_docarray):
    async for resp in client.post(
        '/stop',
        parameters={
            'name_docarray': name_docarray
        },
    ):
        print(resp)

def stop_click_handler():
    asyncio.run(stop_prompt_handler(st.session_state.name_docarray))
    if st.session_state.create_task:
        st.session_state.create_task.cancel()
    if st.session_state.preview_task:
        st.session_state.preview_task.cancel()
    st.stop()
    # st.experimental_rerun()
    
    # asyncio.to_thread(blocking_disco_request(st.session_state.text_prompts, st.session_state.name_docarray))

    # for a in st.session_state.create_request:
    #     a.summary()
    #     a[0].summary()
    #     st.image(image=a[0].uri)


# Receive the variables with streamlit

# Variables for the GUI
st.session_state["input_help"] = ""

def main():
    # st.session_state['cut_ic_pow'] = 1
    # st.session_state['clamp_max'] = 0.05
    # st.session_state['clip_guidance_scale'] = 5000
    # st.session_state['skip_steps'] = 0

    textinput_left.text_input(label="Input Prompt", key="text_prompts", placeholder="A beautiful painting of a singular lighthouse, yellow color scheme")
    textinput_right.text("")
    textinput_right.text("")
    textinput_right.button(label="Start", on_click=click_handler, type="primary")

    left.number_input(label="Sampling Steps:", min_value=10, max_value=300, value=STEPS_DEFAULT, key="steps")

    left.number_input(label="Width:", min_value=100, max_value=1024, value=500, key="width")

    left.number_input(label="Height:", min_value=100, max_value=1024, value=500, key="height")

    left.text_input(label="Seed:", key="seed",  help="The seed to use, if left blank a random seed will be generated.")
    
    advanced_settings = left.expander("Advanced Settings", expanded=False)

    advanced_settings.number_input(label="tv_scale:", min_value=0, max_value=500000, value=TV_SCALE_DEFAULT, key="tv_scale")

    advanced_settings.number_input(label="sat_scale:", min_value=0, max_value=500000, value=SAT_SCALE_DEFAULT, key="sat_scale")

    advanced_settings.number_input(label="cutn_batches:", min_value=1, max_value=16, value=CUTN_BATCHES_DEFAULT, key="cutn_batches")

    advanced_settings.text_input(label="cut_overview:", value=CUT_OVERVIEW_DEFAULT, key="cut_overview")

    advanced_settings.text_input(label="cut_innercut:", value=CUT_INNERCUT_DEFAULT, key="cut_innercut")

    advanced_settings.text_input(label="cut_icgray_p", value=CUT_ICGRAY_P_DEFAULT, key="cut_icgray_p")

    advanced_settings.number_input(label="cut_ic_pow:", min_value=0, max_value=100, value=CUT_IC_POW_DEFAULT, key="cut_ic_pow", help="Higher Values = More Detail")

    advanced_settings.number_input(label="clamp_max:", min_value=0.0, max_value=1.0, value=CLAMP_MAX_DEFAULT, key="clamp_max", help="Increasing this value helps with saturation, increased contrast, and detail.")

    advanced_settings.number_input(label="clip_guidance_scale:", min_value=0, max_value=500000, value=CLIP_GUIDANCE_SCALE_DEFAULT, key="clip_guidance_scale", help="This parameter guides how much Disco stays true to the prompt during the production of the image.")

    advanced_settings.number_input(label="eta:", min_value=0.0, max_value=1.0, value=ETA_DEFAULT, key="eta")

    # advanced_settings.number_input(label="skip_steps:", min_value=0, max_value=300, value=SKIP_STEPS_DEFAULT, key="skip_steps", help="This is the number of steps you skip ahead when starting a run.")

    prompt_settings = left.expander("Prompt Settings", expanded=True)

    # prompt_settings.button(label="Rerun Preview", on_click=preview_click_handler(st.session_state.name_docarray))

    prompt_settings.button(label="Stop prompt", on_click=stop_click_handler)

    left.text("Current Image ID:")
    left.text(st.session_state.name_docarray)

    model_settings = right.expander("Model Settings:", expanded=True)
    model_settings.selectbox("Diffusion Model:", 
        options=DIFFUSION_MODELS,
        index=1,
        key="diffusion_model",
        )
    
    model_settings.checkbox("Use Secondary Model:", value=True, key="use_secondary_model")

    model_settings.multiselect("Clip Models:",
        options=CLIP_MODELS,
        default=["ViT-B-32::openai","ViT-B-16::openai","RN50::openai"],
        key="clip_models")

    # Init Images
    init_image = right.expander("Init Image:", expanded=False)

    init_image.file_uploader(label="Upload Image", type=["png", "jpg", "jpeg"], key="init_image")

    init_image.number_input(label="skip_steps:", min_value=0, max_value=300, value=SKIP_STEPS_DEFAULT, key="skip_steps", help="This is the number of steps you skip ahead when starting a run.")
    
    init_image.number_input(label="init_scale:", min_value=0, max_value=1000, value=INIT_SCALE_DEFAULT, key="init_scale")

    # GIF Settings
    gif_settings = right.expander("GIF Settings:", expanded=False)

    gif_settings.number_input(label="GIF FPS:", min_value=10, max_value=60, value=GIF_FPS_DEFAULT, key="gif_fps")

    save_rate_maximum = st.session_state.get('steps', default = STEPS_DEFAULT) - st.session_state.get('skip_steps', default = SKIP_STEPS_DEFAULT)

    gif_settings.number_input(label="Save Rate:", min_value=1, max_value=save_rate_maximum, value=SAVE_RATE_DEFAULT, key="save_rate")

    # past_image = past_images_tab.empty()
    # left_past_images_tab, right_past_images_tab = past_images_tab.columns([10,1])
    
    past_images_tab.text_input(label="Image ID", key="past_image_name_docarray", placeholder="mydisco-***")
    past_images_tab.button(label="Load Past Image", on_click=past_image_click_handler, args=(st.session_state.past_image_name_docarray,))
    

if __name__ == "__main__":
    # asyncio.run(main())
    main()
