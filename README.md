# 🧹 Discord Message Purger Selfbot

![CLI Preview](preview_v2.png)

**Discord Message Purger Selfbot** is a state-of-the-art, high-performance utility designed for meticulous digital housekeeping on Discord. Built with an asynchronous architecture and a sleek, interactive terminal interface, it offers unparalleled control over your message history. Whether you're conducting a deep cleanup of legacy content or monitoring channels in real-time, this tool provides the precision and speed required for professional-level channel management.

**Discord Message Purger Selfbot** to zaawansowane, wysokowydajne narzędzie stworzone do precyzyjnego zarządzania historią wiadomości na Discordzie. Dzięki asynchronicznej architekturze i nowoczesnemu, interaktywnemu interfejsowi terminalowemu (Rich TUI), oferuje pełną kontrolę nad Twoim cyfrowym śladem. Niezależnie od tego, czy przeprowadzasz głębokie czyszczenie historycznych treści, czy monitorujesz kanały w czasie rzeczywistym, to narzędzie zapewnia precyzję i szybkość klasy profesjonalnej.

> [!CAUTION]
> **DISCLAIMER**: Using self-bots is against Discord's Terms of Service. This tool is for educational purposes only. Use it at your own risk; your account may be permanently banned.

## ✨ Features

- **Deep History Scanning**: Traverse entire channel histories without arbitrary limits.
- **Word Purging**: Delete all messages containing specific keywords or phrases.
- **Thread Support**: Automatically scans and cleans up messages within active threads.
- **Stealth Mode**: Operations are completely silent on the channel; command invocations are immediately deleted.
- **Auto-Delete (Watch Mode)**: Real-time monitoring and immediate deletion of new messages from a target user.
- **Safe Rate Limiting**: Intelligent delays and automatic retry logic to minimize 429 errors.
- **Rich CLI**: A beautiful, colorful terminal interface with real-time feedback.
- **Private Reporting**: Get detailed execution summaries delivered straight to your DMs.

## 🛠️ Installation

### 📱 Android (Termux)
1. **Prepare Environment**:
   ```bash
   pkg update && pkg upgrade
   pkg install python git
   ```
2. **Clone and Setup**:
   ```bash
   git clone https://github.com/GH0ST-codes-pl/Discord-Purger-Selfbot.git
   cd Discord-Purger-Selfbot
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements_purger.txt
   ```

### 🍎 macOS / 🐧 Linux
1. **Clone the repository**:
   ```bash
   git clone https://github.com/GH0ST-codes-pl/Discord-Purger-Selfbot.git
   cd Discord-Purger-Selfbot
   ```
2. **Run Setup Script**:
   ```bash
   chmod +x setup_purger.sh
   ./setup_purger.sh
   ```

### 🪟 Windows
1. **Clone the repository**:
   ```powershell
   git clone https://github.com/GH0ST-codes-pl/Discord-Purger-Selfbot.git
   cd Discord-Purger-Selfbot
   ```
2. **Run Setup Script**:
   - Double-click `setup_purger.bat` or run it via CMD/PowerShell.

### ⚙️ Configuration (All Platforms)
1. Rename `.env.example` to `.env`.
2. Insert your **User Token** into `DISCORD_BOT_TOKEN`.
3. *Tutorial: [How to get Discord Token](https://www.youtube.com/results?search_query=how+to+get+discord+user+token)*.

## 🚀 Usage

### macOS / Linux / Termux:
```bash
./venv/bin/python purger_bot.py
```

### Windows:
```powershell
venv\Scripts\python purger_bot.py
```

### Commands

| Command | Usage | Description |
| :--- | :--- | :--- |
| `.purge_user` | `.purge_user [@User] [limit]` | Deletes messages from a user. If none, cleans your own. Set limit to `0` for full scan. |
| `.purge_word` | `.purge_word <word> [limit]` | Deletes messages containing a specific word. Set limit to `0` for full scan. |
| `.purge_media` | `.purge_media [limit]` | Deletes messages containing attachments/media. |
| `.purge_links` | `.purge_links [limit]` | Deletes messages containing URLs. |
| `.purge_since` | `.purge_since <YYYY-MM-DD>` | Deletes all messages sent after a specific date. |
| `.watch_user` | `.watch_user @User` | Toggles real-time auto-deletion of new messages from @User. |
| `.watch_word` | `.watch_word <word>` | Toggles real-time auto-deletion of messages containing <word>. |
| `.whitelist` | `.whitelist <add/remove/clear>` | Protects specific message IDs from being deleted. |
| `.speed` | `.speed <safe/fast/insane>` | Adjusts the deletion delay (Safe=2.2s, Fast=1.2s, Insane=0.5s). |
| `.multipurge` | `.multipurge #c1 #c2` | Executes a purge of your own messages across multiple channels. |
| `.shutdown` | `.shutdown` | Gracefully stops and closes the selfbot. |

### Komendy (PL)

| Komenda | Użycie | Opis |
| :--- | :--- | :--- |
| `.purge_user` | `.purge_user [@User] [limit]` | Usuwa wiadomości użytkownika. Domyślnie Twoje. Limit `0` = cała historia. |
| `.purge_word` | `.purge_word <słowo> [limit]` | Usuwa wiadomości zawierające konkretne słowo. |
| `.purge_media` | `.purge_media [limit]` | Usuwa wiadomości zawierające załączniki/media. |
| `.purge_links` | `.purge_links [limit]` | Usuwa wiadomości zawierające linki URL. |
| `.purge_since` | `.purge_since <RRRR-MM-DD>` | Usuwa wszystkie wiadomości wysłane po konkretnej dacie. |
| `.watch_user` | `.watch_user @User` | Włącza/wyłącza monitorowanie i usuwanie nowych wiadomości @User. |
| `.watch_word` | `.watch_word <słowo>` | Włącza/wyłącza monitorowanie i usuwanie wiadomości z danym słowem. |
| `.whitelist` | `.whitelist <add/remove/clear>` | Chroni wybrane wiadomości (po ID) przed usunięciem. |
| `.speed` | `.speed <safe/fast/insane>` | Zmienia prędkość usuwania (Safe=2.2s, Fast=1.2s, Insane=0.5s). |
| `.multipurge` | `.multipurge #k1 #k2` | Czyści Twoje wiadomości na wielu kanałach jednocześnie. |
| `.shutdown` | `.shutdown` | Bezpiecznie wyłącza i zamyka bota. |

### Przykłady (Examples)
- `.purge_user @Troll 0` — Completely wipes every message from @Troll.
- `.purge_word "bad word" 0` — Deletes all messages containing "bad word".
- `.purge_since 2024-01-01` — Deletes everything from the beginning of 2024.
- `.watch_word spam` — Immediately deletes any new message containing "spam".
- `.speed insane` — Maximum deletion speed (use with caution!).
- `.multipurge #general #lounge` — Cleans your history in both channels.

### 🛡️ Permission Mode (Auto-Detect)
The bot automatically detects your permissions on the server. 
- **Admin/Manage Messages**: Performs a full purge of all matching messages.
- **Normal User**: Automatically enters **"Personal Mode"**, filtering and deleting only **your own** messages (links, media, words) to avoid permission errors.

### 🛡️ Tryb Uprawnień (Autowykrywanie)
Bot automatycznie wykrywa Twoje uprawnienia na kanale.
- **Admin/Zarządzanie**: Pełne czyszczenie wszystkich pasujących wiadomości.
- **Zwykły Użytkownik**: Automatycznie włącza **"Tryb Osobisty"**, usuwając tylko **Twoje własne** wiadomości (linki, media, słowa), dzięki czemu bot działa bez błędów nawet bez uprawnień administratora.

## 💖 Support

If you find this tool helpful, you can support the developer via Tipply:
[Tipply - @daily-shoty](https://tipply.pl/@daily-shoty)

---
*Created by [GH0ST](https://github.com/GH0ST-codes-pl)*
