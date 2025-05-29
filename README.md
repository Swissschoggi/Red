# 🔴 Red

**Red** is a simple project created during school time a true commie Discord bot for your server of revolutionaries! 🚩

## ✨ Features

Supports **slash** (`/`) commands only:

### 📢 Informational
```
/quote          - Sends a random communist quote
/fact           - Sends a historical communist fact
/randomfigure   - Sends a revolutionary figure
/reactionary    - Sends a random reactionary comment from my TikTok
/reading        - Send a random reading recommendation
/debunk         - Debunks anti-communist myths
/tankiemeter    - Measures your tankie level (saved score)
/asklenin       - Ask Comrade Lenin (running on my local LLM dont know how long i'll keep that in)
```

### 🛠️ Moderation
```
/setdailyquotes - Sends a daily quote to a specified channel (with optional role)
/stopdaily      - Stops daily quotes
/studygroup     - Creates a temporary voice channel for book study groups
```

### 🎭 Fun
```
/reporttrotskyist - Report a user as a Trotskyist
/reporttankie     - Report a user as a Tankie
/gulag            - Sends a user to the GULAG (timeout)
```

### 🗳️ Elections
```
/election_start           - Start elections for something
/election_nominate        - Nominate yourself or others
/election_vote            - Vote for nominated candidates
/election_status - Shows current status of an election
```

---

## 📎 Add the bot

[Add Red to your server](https://discord.com/oauth2/authorize?client_id=1376840332578132069&permissions=8&integration_type=0&scope=bot+applications.commands)

---

## 🛠️ Self-Hosting

### Docker

You can run Red using Docker:

```bash
docker run -d --name red-bot \
  --env-file .env \
  -v $(pwd):/app \
  swissschoggi/red:latest
```

---

## 🗳️ Suggestions Welcome!

**Always open for recommendations to improve the bot** features, quotes, debunks, or historical events!

📬 Contact: `fynninyoass` on Discord
