import streamlit as st
from jina import Client, Executor, requests, DocumentArray
import os
import asyncio
from random import randint 

st.set_page_config(page_title="Disco Diffusion", page_icon="🎨")
st.title('Disco Diffusion')
# form = st.form("prompt_form")
textinput_left, textinput_right = st.columns([10, 1])
left, right = st.columns([1, 2])
image_preview_tab_container = right.tabs(["Image Preview"])
image_preview_tab = image_preview_tab_container.container()

# ENV Variables
HOST_LOCATION = os.environ['SERVER_LOCATION']

# Initialize session state
# st.session_state['create_request'] = []
st.session_state['name_docarray'] = "mydisco-" + str(randint(0, 1000))

client = Client(host=HOST_LOCATION, asyncio=True)

create_response_array = []

async def disco_request(text_prompts: list, name_docarray: str):

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
            'width_height': [st.session_state.width, st.session_state.height]
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
    preview_image = image_preview_tab.empty()
    while len(preview_response_array) < 1 or not completed:
        # print("Waiting for preview response")
        await asyncio.sleep(1)
        await preview_handler(st.session_state.name_docarray)
        # print("current length: " + str(len(preview_response_array)))
        # print("Waiting 1 second")
        # Add the image to preview
        if len(preview_response_array) > 0:
            latest_document = preview_response_array[-1]
            preview_image.image(image=latest_document.uri)
            completed = latest_document.tags["_status"]["completed"] is True


async def prompt_handler():
    text_prompt_array = st.session_state.text_prompts.split(",")

    create_task = asyncio.create_task(disco_request(text_prompt_array, st.session_state.name_docarray))

    # asyncio.to_thread(blocking_disco_request(st.session_state.text_prompts, st.session_state.name_docarray))
    
    await asyncio.gather(
        create_task,
        preview_handler_wait()
    )

    # if len(preview_response_array) > 0:
    #     form.image(image=preview_response_array[0][0].uri)
    # else:
    if len(preview_response_array) < 1:
        form.write("Error")
    # await preview_handler_wait()

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
        form.error("Please input a prompt")
        # text_input.help = "Please input a prompt"
    else:
        asyncio.run(prompt_handler())
    
    # asyncio.to_thread(blocking_disco_request(st.session_state.text_prompts, st.session_state.name_docarray))

    # for a in st.session_state.create_request:
    #     a.summary()
    #     a[0].summary()
    #     st.image(image=a[0].uri)


# Receive the variables with streamlit

# Variables for the GUI
st.session_state["input_help"] = ""

def main():

    textinput_left.text_input(label="Input Prompt", key="text_prompts", placeholder="A beautiful painting of a singular lighthouse, yellow color scheme")
    textinput_right.text("")
    textinput_right.text("")
    textinput_right.button(label="Start", on_click=click_handler, )

    left.number_input(label="Sampling Steps:", min_value=10, max_value=300, value=200, key="steps")

    left.number_input(label="Width:", min_value=100, max_value=1024, value=500, key="width")

    left.number_input(label="Height:", min_value=100, max_value=1024, value=500, key="height")

    left.text_input(label="Seed:", key="seed",  help="The seed to use, if left blank a random seed will be generated.")
    

    left.text("Current Image ID:")
    left.text(st.session_state.name_docarray)


if __name__ == "__main__":
    # asyncio.run(main())
    main()
