# 🌍 Ubuntu-Inspired Image Fetcher

> _"I am because we are."_ — Ubuntu Philosophy

This project embodies the spirit of Ubuntu by connecting to the global web community, respectfully fetching shared images, and organizing them for future appreciation. It’s a practical, respectful, and community-minded tool built with Python.

---

## 📌 Features

- ✅ Prompts user for an image URL
- 📁 Creates a `Fetched_Images` directory if it doesn't exist
- 📥 Downloads and saves the image with a smart filename
- 🛡️ Handles errors gracefully (invalid URLs, timeouts, HTTP errors)
- 🧠 Infers file extensions from content type
- 🔄 Avoids overwriting by auto-incrementing filenames

---

## 🛠️ Requirements

- Python 3.8+
- `requests` library

Install dependencies:

```bash
pip install -r requirements.txt
