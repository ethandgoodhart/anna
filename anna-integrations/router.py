import fastapi
from imessage.iMessage import app as imessage_app
from spotify.main import app as spotify_app
from websearch.main import app as websearch_app
from phone.main import app as phone_app
from canvas.main import app as canvas_app
import subprocess
import os

app = fastapi.FastAPI()

app.mount("/imessage", imessage_app)
app.mount("/spotify", spotify_app)
app.mount("/websearch", websearch_app)
app.mount("/phone", phone_app)
app.mount("/canvas", canvas_app)

if __name__ == "__main__":
    import uvicorn

    current_dir = os.path.dirname(os.path.abspath(__file__))
    node_script_path = os.path.join(current_dir, "phone", "outbound.js")
    
    if not os.path.exists(os.path.join(current_dir, "phone", "node_modules")):
        subprocess.run(["bun", "i"], cwd=os.path.join(current_dir, "phone"))

    subprocess.Popen(["bun", node_script_path])

    uvicorn.run(app, host="0.0.0.0", port=8000)
