import streamlit as st
from jina import Client, Executor, requests, DocumentArray
import os
import asyncio
from random import randint
from yaml import Loader, load as load_yaml

st.set_page_config(page_title="Disco Diffusion UI", page_icon="🎨", layout="wide")
st.title('Disco Diffusion UI')
# form = st.form("prompt_form")
textinput_left, textinput_right = st.columns([10, 1])
left, center, right = st.columns([1, 3, 1])
[image_preview_tab, past_images_tab] = center.tabs(["Image Preview", "Past Images"])
# image_preview_tab_container = image_preview_tab.container()

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

CUT_IC_POW_DEFAULT = 1
CLAMP_MAX_DEFAULT = 0.05
CLIP_GUIDANCE_SCALE_DEFAULT = 5000
SKIP_STEPS_DEFAULT = 0

async def disco_request(text_prompts: list, name_docarray: str):

    cut_ic_pow = st.session_state.cut_ic_pow if ('cut_ic_pow' not in st.session_state) else CUT_IC_POW_DEFAULT
    clamp_max = st.session_state.clamp_max if ('clamp_max' not in st.session_state) else CLAMP_MAX_DEFAULT
    clip_guidance_scale = st.session_state.clip_guidance_scale if ('clip_guidance_scale' not in st.session_state) else CLIP_GUIDANCE_SCALE_DEFAULT
    skip_steps = st.session_state.skip_steps if ('skip_steps' not in st.session_state) else SKIP_STEPS_DEFAULT

    async for resp in client.post(
        '/create',
        parameters={
            'name_docarray': name_docarray,
            'text_prompts': text_prompts,
            'batch_size': 1,
            'cutn_batches': 1,
            'n_batches': 1,
            'seed': st.session_state.seed,
            'steps': st.session_state.steps,
            'width_height': [st.session_state.width, st.session_state.height],
            'diffusion_model': st.session_state.diffusion_model,
            'clip_models': st.session_state.clip_models,
            'use_secondary_model': st.session_state.use_secondary_model,
            'clip_guidance_scale': clip_guidance_scale,
            'cut_ic_pow': cut_ic_pow,
            'clamp_max': clamp_max,
            'skip_steps': skip_steps,
        },
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
            progress_bar.progress((latest_document.tags["_status"]["step"] + 1) / st.session_state.steps)
            preview_image.image(image=latest_document.uri)
            st.session_state["seed_record"] = str(int(latest_document.tags['seed']))
            completed = latest_document.tags["_status"]["completed"] is True
            st.session_state.status = 'completed'


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
        prompt_details.write("Clip Guidance Scale: " + str(st.session_state.clip_guidance_scale))

    # done, pending = await asyncio.wait({create_task})

    # while create_task in pending:
    #     print("Pending")
    #     await asyncio.sleep(1)

    # if create_task in done:
    #     print("Done once")
    
    # if create_task in pending:
    #     print("Pending once")

def click_handler():
    if st.session_state.text_prompts == "":
        textinput_left.error("Please input a prompt")
        # text_input.help = "Please input a prompt"
        return
    if st.session_state.skip_steps > st.session_state.steps:
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

    left.number_input(label="Sampling Steps:", min_value=10, max_value=300, value=200, key="steps")

    left.number_input(label="Width:", min_value=100, max_value=1024, value=500, key="width")

    left.number_input(label="Height:", min_value=100, max_value=1024, value=500, key="height")

    left.text_input(label="Seed:", key="seed",  help="The seed to use, if left blank a random seed will be generated.")
    
    advanced_settings = left.expander("Advanced Settings", expanded=True)

    advanced_settings.number_input(label="cut_ic_pow:", min_value=0, max_value=CUT_IC_POW_DEFAULT, value=1, key="cut_ic_pow", help="Higher Values = More Detail")

    advanced_settings.number_input(label="clamp_max:", min_value=0.0, max_value=1.0, value=CLAMP_MAX_DEFAULT, key="clamp_max", help="Increasing this value helps with saturation, increased contrast, and detail.")

    advanced_settings.number_input(label="clip_guidance_scale:", min_value=0, max_value=500000, value=CLIP_GUIDANCE_SCALE_DEFAULT, key="clip_guidance_scale", help="This parameter guides how much Disco stays true to the prompt during the production of the image.")

    advanced_settings.number_input(label="skip_steps:", min_value=0, max_value=300, value=SKIP_STEPS_DEFAULT, key="skip_steps", help="This is the number of steps you skip ahead when starting a run.")

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
    
    # past_image = past_images_tab.empty()
    # left_past_images_tab, right_past_images_tab = past_images_tab.columns([10,1])
    
    past_images_tab.text_input(label="Image ID", key="past_image_name_docarray", placeholder="mydisco-***")
    past_images_tab.button(label="Load Past Image", on_click=past_image_click_handler, args=(st.session_state.past_image_name_docarray,))
    

if __name__ == "__main__":
    # asyncio.run(main())
    main()
