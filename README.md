**Database Assignment – Task 1 Documentation**

**1.	Set Up the Project Environment**
- Created a project folder and opened it in VS Code
- Ensured Python was installed and working _**(python --version)**_
- Verified the Python extension was installed in VS Code

**2.	Creating and Activating a Virtual Environment**
- Created a virtual environment using _**python – m venv env **_
- Activated the environment with _**env\Scripts\activate**_

**4.	Installed Required Dependencies** 
- Fastapi - _**pip install fastapi**_
- Uvicorn – _**pip install uvicorn**_
- Motor – _**pip install motor**_
- Pydantic – _**pip install pydantic**_
- Python-dotenv – _**pip install python-dotenv**_
- Requests – _**pip install requests**_
- After installation, I saved the list using _**pip freeze > requirements.txt**_

**5.	Created the API Using FastAPI**
- Created a file called **main.py**
- Pasted the starter code from Appendix B (Python FastAPI Code Example)
- Ran the FastAPI Server with _**uvicorn main:app –reload**_
- Tested it by opening **http://127.0.0.1:8000/docs**

**6.	GitHub**
- Created a private GitHub repository 
- Initialised a git repo _**- git init**_
- Added a remote origin to GitHub – _**git remote add origin https://github.com/nic227/Database-Assignment.git**_
- Committed and pushed everything to GitHub:
  - _**git add .**_
  - _**git commit -m "Initial Commit: Task 1"**_
  - _**git branch -M main**_
  - _**git push -u origin main**_




