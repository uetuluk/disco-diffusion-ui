import streamlit as st
from jina import Client, Executor, requests, DocumentArray, Flow
import os
import asyncio
from random import randint 

st.title('Disco Diffusion')

# ENV Variables
HOST_LOCATION = os.environ['SERVER_LOCATION']

# Initialize session state
st.session_state['create_request'] = []
st.session_state['name_docarray'] = "mydisco-" + str(randint(0, 1000))


## Functions

request_state = {"state": ""}

async def disco_request(text_prompts: list, name_docarray: str):
    
    client = Client(host=HOST_LOCATION, asyncio=True)
    
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
        print("Created")

async def preview_handler(name_docarray: str):

    client = Client(host=HOST_LOCATION, asyncio=True)
    
    async for resp in client.post(
        '/result',
        parameters={
            'name_docarray': name_docarray
        },
    ):
        st.session_state.create_request.append(resp)
        

def click_handler():
    with Flow():
        name_docarray = st.session_state.name_docarray
        asyncio.run(disco_request(st.session_state.text_prompts, name_docarray))
        asyncio.run(preview_handler(name_docarray))

        for a in st.session_state.create_request:
            a.summary()
            a[0].summary()
            st.image(image=a[0].uri)


# Receive the variables with streamlit

async def main():
    st.text_input(label="Please input the prompts", key="text_prompts")

    st.button(label="Start", on_click=click_handler)

    st.text(st.session_state.name_docarray)


if __name__ == "__main__":
    asyncio.run(main())