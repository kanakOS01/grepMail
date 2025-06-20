# 📬 grepmail

**Semantic email search using vector embeddings, MindsDB, and local LLMs**

grepmail is a terminal-based CLI app that lets you **search your emails using natural language** queries. It connects to your mailbox, stores email data as vector embeddings, and allows for intelligent querying using a local MindsDB server.

![grepmail demo](https://img.shields.io/badge/built%20with-mindsdb-blueviolet?style=flat\&)

---

## ✨ Features

* 🔍 **AI-powered semantic search** on your inbox
* 💡 Built on top of **MindsDB** + **Typer** + **Rich**
* 📬 Uses your actual emails from any IMAP-compatible provider
* 📀 Local vector storage using PGVector, Ollama for vector embeddings and Gemini for query.

---

## ⚙️ Tech Stack

| Component       | Tech Used                                  |
| --------------- | ------------------------------------------ |
| Language        | Python 3.12+                               |
| CLI Framework   | [Typer](https://typer.tiangolo.com/)       |
| UI Rendering    | [Rich](https://github.com/Textualize/rich) |
| Email Access    | IMAP (via [MindsDB email engine](https://docs.mindsdb.com/integrations/app-integrations/email#email))         |
| Vector Storage  | [MindsDB PGVector store](https://docs.mindsdb.com/integrations/vector-db-integrations/pgvector#pgvector)            |
| Semantic Search | [MindsDB knowledge base](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#knowledge-base) + LLM (Gemini)      |
| Package Manager | [Poetry](https://python-poetry.org/)                                    |

---

## 🧠 MindsDB Usage

This app makes use of the following MindsDB features:
* [**Create KB**](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#create-knowledge-base-syntax): Create a knowledge base to store email data.
* [**Email Engine**](https://docs.mindsdb.com/integrations/app-integrations/email#email): Connects to your email provider via MindsDB's built-in engine
* [**Vector Storage**](https://docs.mindsdb.com/integrations/vector-db-integrations/pgvector#pgvector): Embeds email content as vector chunks using `create vector store`
* [**Knowledge Base**](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#create-knowledge-base-syntax): Stores vectors in a searchable format with MindsDB's `CREATE KNOWLEDGE_BASE`
* [**Natural Language Queries**](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#select-from-kb-syntax): Allows semantic querying using SQL-style syntax over the vector store
* [**Metadata columns**](https://docs.mindsdb.com/mindsdb_sql/knowledge-bases#metadata-columns): Stores email `subject` and `datetime` as metadata.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/kanakOS01/grepmail.git
cd grepmail
```

### 2. Install Dependencies

Install [Poetry](https://python-poetry.org/docs/#installation) (if not installed), then:

```bash
poetry install
```

### 3. Configure Environment

Create a `.env` file in the root of the project. Take reference from `.env.example`.

> ⚠️ Use an **App Password** if your email provider supports it (e.g. Gmail with 2FA). Some reference can be found [here](https://support.google.com/accounts/answer/185833?hl=en).

### 4. Run MindsDB

Make sure MindsDB is running locally on port `47334`. You can setup MindsDB using [Docker](https://docs.mindsdb.com/setup/self-hosted/docker) or using [pip](https://docs.mindsdb.com/setup/self-hosted/pip/source) (which I did for its simplicity)

After setting up MindsDB install the handlers given in `handlers.txt`.

### 5. Setup Postgres

Setup Postgres along with the the PGVector extension.

### 6. Run the CLI App

```bash
poetry run grepmail
```

When running the project for the first time it may take time to load the emails from the email server on to the knowledge base. This happens because of 2 main issues - 
- Email servers take time (40-50 seconds) to connect and get data from.
- The code currently does not have concurrent embedding conversion due to the fact the local ollama runs one instance of the model at a time and therefore the benefit of multi-thread system cannot be accessed without optimizing the code further. Sorry for the incovenience :(

---

## ⁕ Data flow
The code is relatively simple to understand as it a linear flow. But just to give the reader a gist here is how the application functions.
- Create a project `grepmail` if it does not exist.
- Create an email engine to connect with email server if it does not exist.
- Create a knowledge base if it does not exist.
- Create a local email db if it does not exist (as interacting with the email engine is a time taking process).
- When using for the first time insert data from email engine into the knowledge base and local email db (the most time taking step of the process).
- Semantic search on the knowledge base and then query the local email db based on the `id` stored in the knowledge base.
