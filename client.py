from jina import Client
import os

# ENV Variables
HOST_LOCATION = os.environ['SERVER_LOCATION']

# Variables
text_prompts = [
    'A beautiful painting of a singular lighthouse',
    'yellow color scheme',
]

client = Client(host=HOST_LOCATION)

print(client.profiling())

diffusion_request = client.post(
    '/create',
    parameters={
        'name_docarray': 'mydisco-123',
        'text_prompts': text_prompts,
        'batch_size': 1,
        'cutn_batches': 1,
        'steps': 30,
        'width_height': [500, 500]
    },
)

# check intermediate results
diffusion_request = client.post('/result', parameters={'name_docarray': 'mydisco-123'})

# print(diffusion_request)