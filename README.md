# ⚡ InstantShare

A secure, temporary, anonymous file sharing web application built with Flask.

🔗 Live Demo: https://instant-share-31a7.onrender.com/

---

## 🚀 Features

- 📁 Upload files (any type)
- 🔐 6-character unique download code
- 📷 QR code generation for quick access
- ⏳ Auto-expire after 5 minutes
- 🌙 Dark / Light mode toggle
- 📱 Mobile responsive UI
- 🚀 Instant sharing across networks

---

## 🛠 Tech Stack

- Python 3
- Flask
- Gunicorn
- HTML5
- CSS3 (Custom UI)
- JavaScript (AJAX)
- QRCode (Pillow)

---

## 📂 Project Structure

```
instant-share/
│
├── app.py
├── config.py
├── Procfile
├── requirements.txt
│
├── services/
│   └── file_service.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── logo.svg
│
├── templates/
│   └── index.html
│
└── uploads/
```

---

## ⚙️ How It Works

1. User uploads file.
2. Server generates a unique 6-character code.
3. QR code is created.
4. File is temporarily stored.
5. File auto-deletes after download or expiration.

---

## 🧠 Security Features

- Temporary file storage
- Automatic expiration
- No user login required
- No persistent database storage

---

## 📦 Installation (Local Setup)

```bash
git clone https://github.com/aaveshmaan8/instant-share.git
cd instant-share
pip install -r requirements.txt
python app.py
```

Visit:
```
http://127.0.0.1:5000
```

---

## 🌍 Deployment

Deployed on Render using:

```
gunicorn app:app
```

---

## 👨‍💻 Author

**Aavesh Maan**  
B.Tech CSE  
Aspiring Full-Stack Developer

---

## ⭐ Future Improvements

- File size limit control
- Multiple file download support
- File preview before download
- Persistent storage option
- Admin dashboard
