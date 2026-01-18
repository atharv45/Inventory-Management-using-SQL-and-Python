import pandas as pd
import streamlit as st
from db_functions import *

st.sidebar.title('Inventory management dashboard')
selected_task = st.sidebar.radio('Select an option',options=['Basic information' , 'Operational task'])

db = connected_to_db()
cursor = db.cursor(dictionary=True)


if selected_task == 'Basic information':
    st.header('Inventory AND Supply chain management')
    st.header('Basic metrics')
    results = get_basic_information(cursor)

    keys = list(results.keys())
    cols = st.columns(3)

    for i in range(3):
        cols[i].metric(label=keys[i], value=results[keys[i]])

    cols = st.columns(3)

    for i in range(3,6):
        cols[i-3].metric(label=keys[i], value=results[keys[i]])
    st.divider()

    tables = get_additional_tables(cursor)

    for label,query in tables.items():
        st.header(label)
        df = pd.DataFrame(query)
        st.dataframe(df)


if selected_task == 'Operational task':
    st.header('Operational task')

    selected_task = st.selectbox('Select an option',options=['Add New Product', 'Product History', 'Place Reorder'])

    if selected_task == 'Add New Product':
        st.header('Add New Product')
        categories = get_categories(cursor)
        suppliers = get_suppliers(cursor)

        with st.form('Add New Product form'):
            product_name = st.text_input("Product Name")
            product_category = st.selectbox('Category', categories)
            product_price = st.number_input("Product Price", min_value=10)
            product_stock = st.number_input("Stock", min_value=0, step=1)
            product_level = st.number_input("Reorder Level", min_value=0, step=1)

            supplier_ids = [s['supplier_id'] for s in suppliers]
            supplier_name = [s['supplier_name'] for s in suppliers]

            supplier_id = st.selectbox('Supplier ID', options=supplier_ids,
                                       format_func=lambda x:  supplier_name[supplier_ids.index(x)] )
            submitted = st.form_submit_button('Add New Product form')

            if submitted:
                if not product_name:
                    st.error('Product Name is required')
                else:
                    try:
                        add_new_manual_id(cursor,db,product_name,product_category,product_price,product_stock,product_level,supplier_id)
                        st.success('Product Added Successfully')
                    except Exception as e:
                        st.error(e)
    if selected_task == 'Product History':
        st.header('Product History')
        products = get_all_products(cursor)

        product_id = [s['product_id'] for s in products]
        product_name = [s['product_name'] for s in products]
        selected_product_name = st.selectbox('Select Product ID', options=product_name)

        if selected_product_name:
            selected_product_id = product_id[product_name.index(selected_product_name)]
            history_data = get_product_history(cursor,selected_product_id)

            if history_data:
                df = pd.DataFrame(history_data)
                st.dataframe(df)
            else:
                st.info('Product History not found')

    if selected_task == 'Place Reorder':
        st.header('Place Reorder')
        products = get_all_products(cursor)

        product_id = [s['product_id'] for s in products]
        product_name = [s['product_name'] for s in products]
        selected_product_name = st.selectbox('Select Product ID', options=product_name)
        reorder_quantity = st.number_input("Reorder Quantity", min_value=0, step=1)

        if st.button('Place Reorder'):
            if selected_product_name:
                selected_product_id = product_id[product_name.index(selected_product_name)]
                try:
                    place_order(cursor,db,selected_product_id,reorder_quantity)
                    st.success('Product Reordered Successfully')
                except Exception as e:
                    st.error(e)
















