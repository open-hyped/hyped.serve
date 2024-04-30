# Hyped Serve

Hyped Serve is an add-on for [hyped](https://github.com/open-hyped/hyped) designed to streamline the serving process of a hyped data pipeline.

## Installation

You can install the add-on directly from PyPI using pip:

```bash
pip install hyped-serve
```

## Getting Started

Hyped Serve leverages the power of [FastAPI](https://fastapi.tiangolo.com) to create a robust serving environment.

To get started, simply define your data pipeline and its expected input features in a Python script, and then serve it using `hyped.serve`.

Here's a basic example:

```python
# app.py
from hyped.serve import HypedAPI

# Import necessary modules
from hyped import DataPipe, Features
from hyped_serve import HypedAPI

# Define your data pipeline and its expected input features
pipe = DataPipe([...])
features = Features({...})

# Create the app to be served
app = HypedAPI().serve_pipe(pipe, features, prefix="/")
```

Once you've defined your app, you can serve it using uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 80
```
This will start the server, allowing you to interact with your data pipeline via HTTP requests.

## Endpoints

The Hyped Serve API provides the following endpoints for interacting with your data pipeline:

| Endpoint   | Method | Description                                                                                            |
|------------|--------|--------------------------------------------------------------------------------------------------------|
| /health    | GET    | Simple health check always returns "ok" and code 200.                                                  |
| \<prefix\>/ready | GET    | Readiness check to determine if the server is ready to receive requests.                               |
| \<prefix\>/apply | POST   | Process a single example using the data pipeline. Expects a single example in JSON format matching the specified features. |
| \<prefix\>/batch | POST   | Process a batch of examples using the data pipeline. Expects a list of examples.                   |
