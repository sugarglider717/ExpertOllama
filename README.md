# UT Dallas Software Engineering Capstone Project
## Team 7 - Fall 2024

### Instructions
1. Clone the project and navigate to the project directory.
```
git clone https://github.com/SPWilliford/ciobrain-project.git
cd ciobrain-project
```
2. Download and install ollama, available at:
https://ollama.com/download

3. Pull necessary models
```
ollama pull llama3.2
ollama pull nomic-embed-text
```

4. Create CIO_Brain custom model from included Modelfile
```
ollama create CIO_Brain -f ./instance/knowledge/Modelfile
```

5. Create and activate a Python virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```

Create and activate a Python virtual environment (Windows)
```
python -m venv venv
.\venv\Scripts\activate
```

6. Install python dependencies
```
pip install -r requirements.txt
```

7. Start the application
```
flask --app ciobrain run --debug
```

The app should be accessible at http://localhost:5000
