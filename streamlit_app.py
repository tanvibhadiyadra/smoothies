# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col
import pandas as pd

st.title("Customize Your Smoothie! 🥤")
st.write("Build your own smoothie with your favorite ingredients.")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on your Smoothie will be", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

pd_df = my_dataframe.to_pandas()

# Convert to Python list for multiselect
fruit_list = pd_df['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"🔎 Search value for {fruit_chosen}: {search_on}")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            smoothiefroot_response = requests.get(url, timeout=5)

            if smoothiefroot_response.status_code == 200:
                st.dataframe(pd.DataFrame([smoothiefroot_response.json()]), use_container_width=True)
            else:
                st.error(f"API error for {fruit_chosen}: {smoothiefroot_response.status_code}")

        except Exception as e:
            st.error(f"❌ Could not fetch data for {fruit_chosen}")
            st.write(e)

# Insert order into Snowflake
time_to_insert = st.button("Submit Order")

if time_to_insert:
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    session.sql(my_insert_stmt).collect()
    st.success("Your Smoothie is ordered! ✅")
