Smart Student Task & Document Assistant

A web-based AI assistant designed to help students manage tasks, organize academic work, work with documents, and collaborate with teammates.

🚀 Features

🤖 AI Assistant

Generate helpful responses using Google Gemini.

Ask questions and get AI-powered assistance.

Useful for studying, planning, writing, brainstorming, and academic productivity.

API access is handled securely through environment variables.

📋 Smart Task Management

Create and manage student tasks.

Organize academic activities in one place.

Update and delete tasks.

Track shared tasks when working with a team.

👥 Team Collaboration

Create a team with a unique 6-character team code.

Join an existing team using the team code.

Share the same team workspace across devices on the same network.

Display the number of members currently registered in the team.

Member count updates automatically while the page is open.

Leave a team and automatically decrease the member count.

📄 Document Assistance

The project is designed to support student document workflows, making it easier to work with academic content and use AI for productivity.

🌐 Local Network Access

The Flask server can be configured to listen on all network interfaces so teammates connected to the same Wi-Fi/network can access the application.

🛠️ Tech Stack

Frontend: HTML, CSS, JavaScript

Backend: Python, Flask

Database: SQLite

AI: Google Gemini API

Environment Management: python-dotenv

Package Management: pip

📁 Project Structure

student-assistant-full/
│
├── .venv/
│
├── student-assistant/
│   ├── static/
│   │   └── index.html
│   │
│   ├── .env
│   ├── app.py
│   ├── README.md
│   └── requirements.txt
│
└── venv/

⚙️ Requirements

Make sure you have:

Python 3.10+ recommended

pip

A Google Gemini API key

Windows, macOS, or Linux

Internet connection for Gemini API requests

🔧 Installation

1. Open the project folder

In PowerShell:

cd C:\Users\User\Downloads\student-assistant-full\student-assistant

2. Create and activate a virtual environment

If you do not already have one:

python -m venv venv

Activate it on Windows:

.\venv\Scripts\Activate.ps1

3. Install dependencies

pip install -r requirements.txt

🔑 Configure Gemini API

Create a .env file inside the student-assistant folder:

GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.8-flash

Replace YOUR_ACTUAL_GEMINI_API_KEY with your own API key.

Important: Never commit your real API key to GitHub or share it publicly.

▶️ Run the Application

From the project directory:

python app.py

The application should be available at:

http://127.0.0.1:5000

Open that address in your browser.

👥 Using Team Collaboration

Create a Team

Open the Team section.

Select Create Team.

Enter a team name.

Click Create Team.

A unique 6-character team code will be generated.

Example:

AI Warriors
Team Code: K7M4XP
👥 Members joined: 3

Share the team code with your teammates.

Join a Team

Open the Team section.

Select Join Team.

Enter the 6-character team code.

Click Join Team.

You will be connected to the shared team workspace.

Leave a Team

Click Leave Team.

The server removes your registered team member and the displayed member count decreases.

Member Count

The frontend periodically refreshes the team information while the page is open. This allows members on different devices to see changes to the member count.

Note: If a user closes the browser without clicking Leave Team, they may remain registered. Automatic online/offline presence would require a heartbeat/presence system.

🌐 Run for Multiple Devices on the Same Wi-Fi

The Flask server should listen on all network interfaces:

app.run(
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "5000")),
    debug=False
)

Start the server:

python app.py

Find your computer's local IPv4 address:

ipconfig

Look for something similar to:

IPv4 Address. . . . . . . . . . . : 192.168.1.105

Other teammates connected to the same Wi-Fi can open:

http://192.168.1.105:5000

Important

All teammates must connect to the same computer/server if the application is using the local SQLite database. If every teammate runs their own copy of Flask, each copy will have its own local database.

If Windows Firewall blocks access, allow Python through the firewall on the Private network.

🔌 API Overview

The Flask backend provides endpoints for AI and team collaboration.

AI

POST /api/ai

Used to send prompts to the Gemini-powered assistant.

Team

POST /api/team/create
POST /api/team/join
GET  /api/team/<code>/tasks
POST /api/team/<code>/tasks
PATCH /api/team/<code>/tasks/<task_id>
DELETE /api/team/<code>/tasks/<task_id>
POST /api/team/<code>/leave

The team APIs manage team creation, joining, shared tasks, member registration, and leaving a team.

🗄️ Database

The application uses SQLite for local persistence.

The database stores information such as:

Teams

Team tasks

Team members

Team codes are generated using a restricted character set to make them easier to read and share.

Example:

K7M4XP

🔒 Security Notes

Keep .env private.

Never upload your Gemini API key to GitHub.

Do not commit secrets to source control.

The Flask development server is intended for local development/testing.

Do not expose the development server directly to the public internet.

A .gitignore file should include:

.env
venv/
.venv/
__pycache__/
*.pyc
*.db
*.sqlite
*.sqlite3

🧪 Troubleshooting

requirements.txt not found

Make sure you are inside:

student-assistant

Then run:

pip install -r requirements.txt

Gemini returns 503 UNAVAILABLE

A 503 response can occur when the selected Gemini model is temporarily unavailable or experiencing high demand.

Check that:

GEMINI_API_KEY is loaded correctly.

Your internet connection works.

The configured Gemini model is currently available.

The API service is not experiencing temporary capacity issues.

Teammate cannot open the website

Check:

Both devices are on the same Wi-Fi/network.

Flask is running with host="0.0.0.0".

You are using the host computer's IPv4 address.

Windows Firewall is not blocking Python.

Port 5000 is accessible on the local network.

Member count does not change

The current system counts registered members who have not clicked Leave Team.

If a browser is simply closed, that member can remain registered. A future heartbeat/presence feature can automatically mark inactive members as offline.

💡 Future Improvements

Possible future features include:

Automatic online/offline presence using heartbeats

User accounts and authentication

Real-time WebSocket updates

PDF/DOCX document upload and analysis

AI-generated summaries and study notes

Assignment deadline reminders

Calendar integration

Team chat

Role-based team permissions

Cloud database support

Deployment to a cloud platform

More advanced AI agents for multi-step student workflows

🎯 Hackathon Track

Track: Agentic AI

The project can be extended into an agentic student assistant that can:

Understand a student's request.

Plan the required steps.

Use available tools.

Work with tasks and documents.

Produce useful results.

Keep the student in control through human review and confirmation.

📜 License

This project is intended for educational, hackathon, and demonstration purposes.
