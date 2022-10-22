import streamlit as st
from jina import Client, Executor, requests, DocumentArray
import os
import asyncio
from random import randint 

st.title('Disco Diffusion')

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
            'steps': 10,
            'width_height': [500, 500]
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
        print(name_docarray)
        print(resp)
        print(resp.summary())
        if len(resp) > 0:
            print(resp[0])
            print(resp[0].summary())
            preview_response_array.append(resp)
        # if resp.length > 0:
        #     print(resp[0])
        #     print(resp[0].summary())
    # await asyncio.sleep(1)

    

async def preview_handler_wait():
    # preview_task = asyncio.create_task(preview_handler(st.session_state.name_docarray))
    # print("Running the preview handler wait loop")
    while len(preview_response_array) < 1:
        # print("Waiting for preview response")
        await asyncio.sleep(1)
        await preview_handler(st.session_state.name_docarray)
        # print("current length: " + str(len(preview_response_array)))
        # print("Waiting 1 second")
        

async def prompt_handler():
    create_task = asyncio.create_task(disco_request(st.session_state.text_prompts, st.session_state.name_docarray))

    # asyncio.to_thread(blocking_disco_request(st.session_state.text_prompts, st.session_state.name_docarray))
    
    await asyncio.gather(
        create_task,
        preview_handler_wait()
    )

    if len(preview_response_array) > 0:
        st.image(image=preview_response_array[0][0].uri)
    else:
        st.write("Error")
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
    asyncio.run(prompt_handler())
    
    # asyncio.to_thread(blocking_disco_request(st.session_state.text_prompts, st.session_state.name_docarray))

    # for a in st.session_state.create_request:
    #     a.summary()
    #     a[0].summary()
    #     st.image(image=a[0].uri)


# Receive the variables with streamlit

def main():
    st.text_input(label="Please input the prompts", key="text_prompts")

    st.button(label="Start", on_click=click_handler)

    st.text(st.session_state.name_docarray)


if __name__ == "__main__":
    # asyncio.run(main())
    main()
