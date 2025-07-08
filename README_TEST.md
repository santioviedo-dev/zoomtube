# Zoom to YouTube Automation

Automate the process of downloading Zoom recordings and uploading them to YouTube, with automatic iframe generation for embedding videos.

## Features

- Download Zoom cloud recordings for all users on a given date.
- Upload single or multiple videos to YouTube as unlisted.
- Prevent duplicate uploads with a log system.
- Generate and manage iframes for embedding uploaded videos.
- Command-line interface for flexible automation.

## Requirements

- Python 3.8+
- Zoom API credentials (Account ID, Client ID, Client Secret)
- YouTube API credentials (`client_secret.json`)
- Google account with YouTube API enabled

## Setup

1. **Clone the repository:**

   ```sh
   git clone [REPO_URL]
   cd zoom-to-youtube
   ```

2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   - Copy `config/.env.example` to `config/.env` and fill in your values.

4. **Add YouTube credentials:**

   - Place your `client_secret.json` in the `config/` directory.

5. **Initial YouTube authentication:**
   ```sh
   python src/youtube/upload_youtube.py --file [PATH_TO_VIDEO]
   ```
   Follow the browser instructions to authorize access.

## Usage

### Download Zoom recordings

```sh
python main.py --action download --date YYYY-MM-DD
```

### Upload videos to YouTube

- Single file:
  ```sh
  python main.py --action upload --file [PATH_TO_VIDEO]
  ```
- All videos in a folder:
  ```sh
  python main.py --action upload --folder [FOLDER_PATH]
  ```
- By date (uploads all videos from a specific date's folder):
  ```sh
  python main.py --action upload --date YYYY-MM-DD
  ```

### Download and upload in one step

```sh
python main.py --action all --date YYYY-MM-DD
```

## Project Structure

```
zoom-to-youtube/
├── config/
│   ├── .env
│   ├── client_secret.json
│   └── token.pickle
├── data/
│   ├── recordings/
│   └── iframes.json
├── logs/
│   └── uploaded.log
├── output/
│   └── iframes_clean.html
├── src/
│   ├── utils/
│   ├── youtube/
│   └── zoom/
├── main.py
└── requirements.txt
```

## Notes

- Videos are uploaded as "unlisted" on YouTube.
- Duplicate uploads are avoided using `logs/uploaded.log`.
- Iframes for embedding are generated in `data/iframes.json` and `output/iframes_clean.html`.
- Very short recordings (<15 seconds) are ignored.

---

Contributions and issues
