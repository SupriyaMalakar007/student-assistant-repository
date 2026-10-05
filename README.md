# Smart Student Task & Document Assistant

Features: smart quick-add, auto "Do next" ranking, focus timer, calendar,
document analyser (summary, keywords, action items, study cards), PDF upload,
AI summary / ask-your-document / AI task split, and a shared team board.

## Install & run
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
# edit .env and set ANTHROPIC_API_KEY
python app.py
```
Open http://127.0.0.1:5000

## Notes
- Personal tasks and focus history are stored in your browser (localStorage).
- The Team tab is shared through the server (SQLite file `team.db`). To let
  teammates on the same network use it, set `HOST=0.0.0.0` in `.env` and share
  `http://<your-ip>:5000`. Each person is asked for a display name once.
- AI features need an Anthropic API key; without it they show "AI unavailable".
  Everything else works without a key.
- PDF upload loads pdf.js from cdnjs, so it needs an internet connection.
- This is a simple development server with no login; do not expose it publicly.
