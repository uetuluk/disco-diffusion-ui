from jina import Client

c = Client(host='grpc://0.0.0.0:51001')

da = c.post(
    '/create',
    parameters={
        'name_docarray': 'mydisco-123',
        'text_prompts': [
            'A beautiful painting of a singular lighthouse',
            'yellow color scheme',
        ],
    },
)

# check intermediate results
da = c.post('/result', parameters={'name_docarray': 'mydisco-123'})