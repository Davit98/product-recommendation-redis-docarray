import functools
import os

import numpy as np
import streamlit as st
from docarray import DocumentArray, Document


# from dotenv import load_dotenv
# load_dotenv()



@st.cache_data
def load_data():
    da = DocumentArray.pull(os.getenv('DATASET_NAME', 'amazon-berkeley-objects-dataset-encoded'), show_progress=True)
    colors = [None] + list({doc.tags['color'] for doc in da})
    categories = [None] + list({doc.tags['product_type'] for doc in da})
    countries = [None] + list({doc.tags['country'] for doc in da})
    max_width = max({int(doc.tags['width']) for doc in da})
    max_height = max({int(doc.tags['height']) for doc in da})
    redis_da = DocumentArray(storage='redis', config={
        # for Redis cloud
        # 'host': 'redis-13273.c266.us-east-1-3.ec2.cloud.redislabs.com',
        # 'port': 13273,
        # 'redis_config': {
        #     'password': os.getenv('REDIS_PASSWORD')
        # },
        'host': 'localhost',
        'port': 6379,
        'n_dim': 768,
        'columns': {
            'color': 'str',
            'country': 'str',
            'product_type': 'str',
            'width': 'int',
            'height': 'int',
            'brand': 'str',
        },
        'tag_indices': ['item_name']
    })
    redis_da.extend(da)
    return redis_da, colors, categories, countries, max_width, max_height


def recommend(view_history, da: DocumentArray, k: int = 8, color=None, category=None, country=None, min_width=None,
              max_width=None, min_height=None, max_height=None):
    user_filter = ''
    if color:
        user_filter += f'@color:{color} '

    if country:
        user_filter += f'@country:{country} '

    if category:
        user_filter += f'@product_type:{category} '

    if max_width or min_width:
        user_filter += f'@width:[{min_width or "-inf"} {max_width or "inf"}] '

    if max_height or min_height:
        user_filter += f'@height:[{min_height or "-inf"} {max_height or "inf"}] '

    if view_history:
        embedding = np.average(
            [doc.embedding for doc in view_history],
            weights=range(len(view_history), 0, -1),
            axis=0
        )
        return da.find(embedding, filter=user_filter, limit=k)
    else:
        return da.find(filter=user_filter, limit=k)


def view(product_id: str, da: DocumentArray):
    image_column, info_column = st.columns(2)
    doc = da[product_id]
    image_column.image(doc.uri)
    info_column.write(f'Name: {doc.tags["item_name"]}')
    info_column.write(f'Category: {doc.tags["product_type"]}')
    info_column.write(f'Country: {doc.tags["country"]}')
    info_column.write(f'Brand: {doc.tags["brand"]}')
    info_column.write(f'Width: {doc.tags["width"]}')
    info_column.write(f'Height: {doc.tags["height"]}')

    del st.session_state['product']


def set_viewed_product(product: Document, k: int = 8):
    st.session_state['product'] = product.id
    view_history = st.session_state.get('view_history', [])
    view_history.insert(0, product)
    view_history = view_history[:k]
    st.session_state['view_history'] = view_history


def view_products(docs, k: int = 8):
    columns = st.columns(k)
    for doc, column in zip(docs[:k], columns):
        container = column.container()
        container.button('view', on_click=functools.partial(set_viewed_product, product=doc, k=k), key=doc.id)
        container.image(doc.uri, use_column_width='always')
