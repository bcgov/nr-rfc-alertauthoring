import src.main
import uvicorn

"""
Normally the app would be run through a command line call to uvicorn.  Sometimes
its useful to start the app inside of a debug session so you can walk through 
the code to help understand what is happening behind the scenes in the various
frameworks utilitized by FastAPI.  

This script allows you to do that.

Open the script in vscode and run as a debug session after having inserted break
points.
"""


uvicorn.run(src.main.app, host="0.0.0.0", port=3000)
