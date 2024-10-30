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
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#convert the Snowpark Dataframe to a pandas dataframe so we could use the LOC function
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()






# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    'Choose upto 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# If ingredients are selected, process the order
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Ensure consistent indentation here
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')

        # Fetch data from Fruityvice API
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # Create insert statement for Snowflake
    my_insert_stmt = f""" 
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit_order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
