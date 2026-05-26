# Installation

Follow these steps to install the project dependencies and prepare the environment.

Prerequisites:

- Python 3.10 or newer installed.
- Git (to clone the repository) — optional if you already have the files.

Installation steps:

1. Clone the repository (if needed) and change into the project directory:

   git clone <repo-url>
   cd blog-api

2. Create a virtual environment:

   python -m venv venv

3. Activate the virtual environment (PowerShell):

   .\venv\Scripts\Activate.ps1

   (Cmd.exe):

   .\venv\Scripts\activate.bat

   (Git Bash / WSL):

   source venv/bin/activate

4. Install Python dependencies:

   pip install --upgrade pip
   pip install -r [requirements.txt](requirements.txt)

5. Copy the example environment file and edit as needed:

   PowerShell: Copy-Item .env.example .env

   Cmd.exe: copy .env.example .env

   (See [ .env.example ](.env.example) for available variables.)

6. Apply database migrations (if applicable):

   alembic upgrade head

That completes installation. For any further setup (runtime, environment-specific configuration, or database credentials), edit the [ .env.example ](.env.example) and follow your deployment-specific steps.
