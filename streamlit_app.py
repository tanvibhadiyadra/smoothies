# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f"Customize Your Smoothie!🥤")
st.write(
  """Build your own smoothie with your favorite ingredients.
  """
)


name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on your Smoothie will be", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'choose up to 5 ingredients:',
    my_dataframe , max_selec
    tions = 5
)
if ingredients_list:
    
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + 'Nutrition Information')        
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                values ('""" + ingredients_string + """','""" + name_on_order + """')"""
 
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")



