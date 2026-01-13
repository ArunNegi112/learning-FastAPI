from fastapi import FastAPI, Path, HTTPException, Query # type: ignore
import json #To load the json data

app = FastAPI()

#Function to load complete data
def load_data():
    '''Loads data of all patients'''
    with open('2_Medical_records_api\patients.json','r') as file:
        data = json.load(file)
    return data

#Function to save data after POST or PUT
def save_data(data):
    with open('2_Medical_records_api\patients.json', 'w') as file:
        json.dump(data,fp=file)

@app.get("/")
def home():
    return {'message': 'Welcome to Medical Records'}


@app.get("/about")
def about():
    return {'message': 'A fully functional API to manage your patient records'}


@app.get("/view")
def view():
    return load_data()


@app.get("/patient/{patient_id}")
def view_patients(patient_id: str = Path(..., description="Enter the patient_id", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient does not exist")


@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="sort on the basis of 'height','bmi', 'age'"), order: str = Query(default='asc',description="ascending or descending")):

    data = load_data()
    valid_keys = ['height','bmi','age']
    valid_order = ['asc','desc']

    if sort_by not in valid_keys:
        raise HTTPException(status_code=400, detail=f"Invalid field, select from {valid_keys}")

    if order not in valid_order:
        raise HTTPException(status_code=400, detail="Invalid order")
    
    sort = False if order=='asc' else True
    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by,0), reverse=sort)
    return sorted_data


"""
What is a 'Request body' 
   The portion of http request sent by client to the server in structured format(JSON, XML, etc). Which is typically used for http methods such as POST or PUT, for the purpose of creating or updating resources on the http server

Now, let the client add some data to server - by adding a new patient 
Steps: 
 1. Get the request body (data) in JSON format
 2. Validate the request body using pydantic models (check out 3_Pydantic)
 3. If the data is correct then add this new record
"""

# Creating pydantic model
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal

class Patient(BaseModel):
    id: Annotated[str, Field(...,description="Enter the ID. Each id represents different patient", examples=['P001','P002'])]
    name: Annotated[str, Field(..., description='Enter the name of patient')]
    age: Annotated[int, Field(..., ge=0, description='Enter the age of patient')]
    city: Annotated[str, Field(..., description='Enter the city of patient is currently living')]
    gender: Annotated[Literal['male','female','others'], Field(..., description='Gender of patient: male,female,others')]
    height: Annotated[float, Field(..., gt=0,description='Height of patient in meters')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of patient in kgs')]

    @computed_field
    @property
    def bmi(self)-> float:
        calculated_bmi = round((self.weight/(self.height ** 2)),2)
        return calculated_bmi
    
    @computed_field
    @property
    def verdict(self)-> float:
        bmi_ = self.bmi
        return 'underweight' if bmi_<18.5 else 'Normal' if bmi_<24.9 else 'overweight' if bmi_< 29.9 else 'obese'
    

from fastapi.responses import JSONResponse
@app.post('/create')
def add_patient(patient: Patient):

    #Load the existing data
    data = load_data()

    #Check if id already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient id already exists. Either check the data again or enter new id')
    
    #Add new patient to the data
    data[patient.id] = patient.model_dump(exclude={'id'})
    save_data(data)

    return JSONResponse(status_code=200, content="Patient details added successfully")



'''
Updating data: PUT method
For this:
1. Take patient id as path parameter
2. Take request body (which contains the new data that is to be put)
3. Create new pydantic model for this (This is because previous Patient model have all fields compulsory and here we dont want that)
'''
from typing import Optional

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(ge=0,default=None)]
    city: Annotated[Optional[str],Field(default=None)]
    gender: Annotated[Optional[Literal['male','female','others']], Field(default=None)]
    height: Annotated[Optional[float], Field(gt=0,default=None)]
    weight: Annotated[Optional[float], Field(gt=0,default=None)]

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, req_body: PatientUpdate):

    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient does not exist")
    
    patient_info = data[patient_id]
    given_patient_info = req_body.model_dump(exclude_unset=True)  #unset values (Fields with value 'None' will be removed)

    for key, value in given_patient_info.items():
        patient_info[key] = value
    
    #Now, variable 'patient_info' contains updated values 
    #But there is one problem, the values of computed_fields are not updated 
    #So, we will pass this new info to the previous Patient model 
    #But before pass this patient_info to Patient model, we need to add field 'id' in it
    pydantic_patient_info = Patient(id=patient_id,**patient_info)
    #And now convert this into dict again

    updated_patient_info = pydantic_patient_info.model_dump(exclude={'id'}) 

    #update this into existing data
    data[patient_id] = updated_patient_info

    #save data
    save_data(data)

    return JSONResponse(status_code=200, content='Data updated successfully')




## DELETE operation on patients
@app.delete('/delete/{patient_id}')
def del_patient(patient_id: str):

    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del data[patient_id]
    save_data(data)

    return JSONResponse(status_code=200, content='Patient deleted successfully')



'''
Project complete. 
All CRUD operations are used
'''