from fastapi import FastAPI # type: ignore

#Create app instance
app = FastAPI()

#declare the route, then function
@app.get('/')
def hellow():
    return {'Message':'Hellow this is home page'}


@app.get('/about')
def about():
    return {'message': 'This is the about page'}


#To run the application
# in the terminal write: "uvicorn 1_Basics.main:app --reload"
# what is reload?- it reloads the webpage automatically everytime i update something