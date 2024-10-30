# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customise your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!.
    """
)

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on smoothie will be:", name_on_order)

# Snowflake connection
cnx= st.connection("snowflake")
session = cnx.session()

# Fetch available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multiselect for choosing ingredients
ingredients_list = st.multiselect('Choose upto 5 ingredients:',
                                  my_dataframe,
                                  max_selections = 5
                                 )

# If ingredients are selected, process the order
if ingredients_list:
    
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    
    time_to_insert = st.button('Submit_order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# Fruityvice API request and display data in a dataframe
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")

# Display the API response data in a dataframe
fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
