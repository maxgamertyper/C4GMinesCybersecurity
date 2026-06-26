from fastapi import FastAPI, status, Body
from server import utility
from server import fileHandler

app = FastAPI()
VERISON = "0.0.1"

# To start the server run "fastapi dev ./src/server/main.py" if in the full repository, otherwise just "fastapi dev"
@app.get("/")
def read_root():
    return {
        "sourceURL": "https://github.com/maxgamertyper/C4GMinesCybersecurity/tree/main",
        "version": VERISON,
        "environment": "production"
        }

@app.get("/health", status_code=status.HTTP_200_OK)
def read_root():
    return {
        "status": "ok", 
        "timestamp": utility.get_time()
        }

#update this as we code tests, should be a string i.e "AI analysis"
@app.get("/tests", status_code=status.HTTP_204_NO_CONTENT)
def read_root():
    return {
        "implementedTests": []
        }


@app.post("/feedback", status_code=status.HTTP_204_NO_CONTENT) #HTTP_204_NO_CONTENT
def read_root(feedback:str = Body(embed=True)): # embeds the feedback field into the variable, could just use the payload as a dict if wanted
    print(feedback)
    fileHandler.write_feedback(feedback)
    return