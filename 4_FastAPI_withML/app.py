from fastapi import FastAPI
from pydantic import BaseModel, Field, computed_field
from fastapi.responses import JSONResponse
from typing import Annotated, Literal
import pickle
import pandas as pd


app = FastAPI()

with open(r'4_FastAPI_withML/model.pkl', 'rb') as file:
    model = pickle.load(file)


tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
"Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
"Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
"Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
"Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
"Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
"Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]

#Create Pydantic model
class UserInput(BaseModel):
    age: Annotated[int, Field(...,description='Enter age of patient')]
    weight: Annotated[float, Field(...,gt=0, description='Enter current weight of patient')]
    height: Annotated[float, Field(...,gt=0, description='Enter height of patient')]
    income_lpa: Annotated[float, Field(...,gt=0, description='Enter income of patient in LPA')]
    occupation: Annotated[Literal['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'], Field(...,description="Enter occupation of patient. Possible values are ['retired', 'freelancer', 'student', 'government_job','business_owner', 'unemployed', 'private_job']")]
    smoker : Annotated[bool, Field(..., description="Does patient smoke? true or false")]
    city : Annotated[str, Field(..., description='Enter city where patient is living')]

    #Now the thing is that, model is trained on features: ['income_lpa', 'occupation', 'age_group', 'bmi', 'city_tier']. 
    #Hence we need to transform given inputs into these values so that we can give it to ML model

    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight/(self.height**2)
           
    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "Adult"
        elif self.age < 60:
            return "middle aged"
        else:
            return "old"


    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3



#Create endpoint
@app.post('/predict')
def predict_premium(data: UserInput):

    #convert data(json) into dataframe 
    data_df = pd.DataFrame([{
        'bmi': data.bmi,
        'age_group': data.age_group,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'smoker': data.smoker,
        'occupation': data.occupation
    }])

    #predict
    prediction = model.predict(data_df)[0]

    return JSONResponse(status_code=200, content={'prediction_category':prediction})
