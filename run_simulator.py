import os
import sys
import uvicorn
import webbrowser
import threading
import time

# Update the import path to ensure backend modules can be found
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Now we can import the FastAPI app
from backend.main import app

def open_browser():
    # Wait for the server to start
    time.sleep(2)
    print("Opening browser...")
    webbrowser.open("http://127.0.0.1:8001")

if __name__ == "__main__":
    # Start a background thread to open the browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("Starting Wavefront Simulator...")
    # Run the uvicorn server
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
