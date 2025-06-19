# 📬 grepmail

**Semantic email search using vector embeddings, MindsDB, and local LLMs**

grepmail is a terminal-based CLI app that lets you **search your emails using natural language** queries. It connects to your mailbox, stores email data as vector embeddings, and allows for intelligent querying using a local MindsDB server.

![grepmail demo](https://img.shields.io/badge/built%20with-mindsdb-blueviolet?style=flat\&logo=openai)

---

## ✨ Features

* 🔍 **AI-powered semantic search** on your inbox
* 💡 Built on top of **MindsDB** + **Typer** + **Rich**
* 📬 Uses your actual emails from any IMAP-compatible provider
* 📀 Local vector storage, no cloud APIs or third-party AI tools
* 🧠 Displays results with subject, sender, recipient, date, and snippet

---

## ⚙️ Tech Stack

| Component       | Tech Used                                  |
| --------------- | ------------------------------------------ |
| Language        | Python 3.12+                               |
| CLI Framework   | [Typer](https://typer.tiangolo.com/)       |
| UI Rendering    | [Rich](https://github.com/Textualize/rich) |
| Email Access    | IMAP (via MindsDB email engine)            |
| Vector Storage  | MindsDB vector store                       |
| Semantic Search | MindsDB knowledge base + LLM               |
| Package Manager | Poetry                                     |

---

## 🧠 MindsDB Usage

This app makes use of the following MindsDB features:

* **Custom Project**: Creates a MindsDB project named `grepmail`
* **Email Engine**: Connects to your email provider via MindsDB's built-in engine
* **Vector Storage**: Embeds email content as vector chunks using `create vector store`
* **Knowledge Base**: Stores vectors in a searchable format with MindsDB's `create knowledge base`
* **Natural Language Queries**: Allows semantic querying using SQL-style syntax over the vector store

You must have **MindsDB running locally** (or remotely), preferably with vector support enabled.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/grepmail.git
cd grepmail
```

### 2. Install Dependencies

Install [Poetry](https://python-poetry.org/docs/#installation) (if not installed), then:

```bash
poetry install
```

### 3. Configure Environment

Create a `.env` file in the root of the project:

```ini
EMAIL_ID=your_email@example.com
EMAIL_PWD=your_email_password_or_app_token
```

> ⚠️ Use an **App Password** if your email provider supports it (e.g. Gmail with 2FA).

---

### 4. Run MindsDB

Make sure MindsDB is running locally on port `47334`.

If not already installed:

```bash
docker run -p 47334:47334 mindsdb/mindsdb
```

---

### 5. Run the CLI App

```bash
poetry run grepmail
```

---

## 🖼 Example CLI Output

```bash
📬 grepMail

Semantic search across your emails using MindsDB, vector embeddings, and local LLMs.

✅ Setup complete! You can now search your emails.
🔍 Enter a semantic email query (or 'exit'): project update from last week

📨 Found 3 matching emails:



```
