# Simple Tree Data API - SNH AI Assignment

This project is a simple, production-ready HTTP server built with Python and FastAPI. It exposes two endpoints to manage tree data structures. Data is persisted between server restarts using a file-based JSON database (TinyDB).

***

## Prerequisites

- Python 3.7+
- pip (Python package installer)

***

## 1. Installation

First, clone the repository and navigate into the project directory. Then, install the required packages.

```bash
# Clone the repository (example)
# git clone <your-repo-url>
# cd <your-repo-directory>

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install "fastapi[all]" tinydb
````

-----

## 2\. Running the Server

To start the HTTP server, run the `main.py` file using the `uvicorn` server:

```bash
uvicorn main:app --reload --port 5001
```

  - `--reload`: Auto reload on changes.
  - `--port`: Specifies the port to run on.

The server will be accessible at `http://127.0.0.1:5001` and a `db.json` file will be created in your directory to store the data.

-----

## 3\. Interactive API Documentation

Once the server is running, you can access the Swagger docs in your browser:

[http://127.0.0.1:5001/docs](http://127.0.0.1:5001/docs)

-----

## 4\. Running the Tests

You can run the included unit tests from your terminal with:

```bash
python -m unittest tests.py
```

-----

## 5\. Using the API

You can use any API client to interact with the endpoints.

### GET /api/tree

Returns an array of all trees that exist in the database.

**Example Request:**

```bash
curl http://127.0.0.1:5001/api/tree
```

**Example Response:**

```json
[
  {
    "id": 1,
    "label": "root",
    "parentId": null,
    "children": [
      {
        "id": 2,
        "label": "child",
        "parentId": 1,
        "children": []
      }
    ]
  }
]
```

### POST /api/tree

Creates a new node. To create a root node, omit the `parentId` field.

**Example Request (Creating a child node):**

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"label": "new child", "parentId": 1}' \
http://127.0.0.1:5001/api/tree
```

**Example Request (Creating a root node):**

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"label": "new root"}' \
http://127.0.0.1:5001/api/tree
```

**Example Success Response (201 Created):**

```json
{
  "id": 3,
  "label": "new child",
  "parentId": 1,
  "children": []
}
```


# Future Plans & Improvements
This project works great for the challenge, but if this were a real app that needed to grow, here’s what I'd do next.

## 1. Switch to a Real Database
I used a simple file (TinyDB) to save the data just to make setup and testing quicker. For a real app with large volume usage, I'd switch to a proper database like PostgreSQL. It's way faster for handling this kind of tree data because it can grab the whole tree structure at once, which is much better than having my code piece it all together.

## 2. Put it in a Docker Container
To make this app easy to run anywhere, I'd wrap it up in a Docker container. That way, it runs the same for all devs and on the final server.

## 3. Make Configuration Easier
Right now, some settings are typed directly into the code. I'd pull those out and use environment variables instead. This would let us change things like the database location or port number without ever touching the code, which is safer and way more flexible for running the app in different places like dev vs live server.

## 4. Organize the Code Better
I kept everything in one file to keep it simple for this project. If this were going to get bigger, I'd break the code up into different files based on what they do (one for API routes, another for database logic, etc.). This just keeps things clean and makes the code easier to manage as new features are added.

## 5. Add More Tests
The tests I wrote check that the main features work as expected. In the future, I'd add more tests for weird situations (edge cases), like what happens if a tree gets super deep or someone sends weird data. I'd also do some load testing to see how the app performs when lots of people are using it at the same time to make sure it stays fast.