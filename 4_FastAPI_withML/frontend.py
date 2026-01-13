import streamlit as st 
import requests

st.title("Insurance Premium Classification")
st.markdown("Enter your details here:")


age = st.number_input("Age", min_value=0)
weight = st.number_input("Weight (kgs)", min_value=1)
height = st.number_input("Height (meters)", min_value=0.1)
income_lpa = st.number_input("Income (LPA)")
smoker = st.selectbox(label='Smoker', options=[True, False])
city = st.text_input(label='City name')
occupation = st.selectbox(label='Occupation', options=['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'])



if st.button("Predict premium class"):
    input_data = {
        'age':age,
        'weight':weight,
        'height':height,
        'income_lpa': income_lpa,
        'smoker':smoker,
        'city': city,
        'occupation': occupation
    }

    try: 
        response = requests.post(url="http://127.0.0.1:8000/predict", json=input_data)
        result = response.json()

        if response.status_code == 200 and result in response :
            prediction = result["prediction_category"]
            st.success(f"Predicted Insurance Premium Category: **{prediction}**")


        else:
            st.error(f"API Error: {response.status_code}")
            st.write(result)

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the FastAPI server. Make sure it's running.")

    

# to run this type "streamlit run 4_FastAPI_withML/frontend.py" (make sure that app.py is running too)