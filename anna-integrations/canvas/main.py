from datetime import datetime
import os
from urllib.parse import urlencode
import requests
from fastapi import FastAPI
import dotenv

dotenv.load_dotenv()

app = FastAPI()

@app.get("/upcoming-assignments")
def get_canvas_assignments():  # course ids would be stored in prod
    BASE_URL = "https://stanford.instructure.com/api/v1"
    courses = requests.get(
        f"{BASE_URL}/courses",
        headers={"Authorization": f"Bearer {os.getenv('CANVAS_API_KEY')}"},
        params={
            "enrollment_type": "student",
            "enrollment_state": "active",
            "state[]": "available"
        }
    ).json()
    result = []

    for course in courses:
        print(f"Course ID: {course['id']}, Name: {course['name']}")
        assignments_url = f"{BASE_URL}/courses/{course['id']}/assignments"
        assignments = requests.get(
            assignments_url,
            headers={"Authorization": f"Bearer {os.getenv('CANVAS_API_KEY')}"}
        ).json()
        assignments_parsed = [
            {
                'class': course['name'],
                'assignment': a['name'],
                'due_at': datetime.strptime(a['due_at'], '%Y-%m-%dT%H:%M:%SZ')
            }
            for a in assignments
            if a["has_submitted_submissions"] == False and a['due_at'] != None
        ]
        result += assignments_parsed
    
    now = datetime.now()
    upcoming = [a for a in result if a['due_at'] > now]
    return sorted(upcoming, key=lambda x: x['due_at'])

if __name__ == "__main__":
    print(get_canvas_assignments())