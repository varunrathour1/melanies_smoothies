import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# Convert the Snowpark DataFrame to a pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Display the DataFrame
st.dataframe(pd_df)

# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),  # Use the FRUIT_NAME column for options
    max_selections=5
)

# If ingredients are selected, process the order
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get the corresponding search value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')

        # Fetch data from Fruityvice API
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
        if fruityvice_response.status_code == 200:
            fv_data = fruityvice_response.json()
            st.json(fv_data)  # Display JSON data in a readable format
        else:
            st.error("Error fetching data from Fruityvice API.")

    # Create insert statement for Snowflake
    my_insert_stmt = f""" 
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    # Submit order button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
