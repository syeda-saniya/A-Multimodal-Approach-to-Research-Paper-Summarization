# A Multimodal Approach to Research Paper Summarization


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need Python installed on your system. The project uses a virtual environment to manage dependencies.

### Installing

Follow these steps to get your development environment running:

1. **Clone the repository**

   Start by cloning the repository to your local machine:

   ```bash
   git clone https://github.com/syeda-saniya/A-Multimodal-Approach-to-Research-Paper-Summarization.git
   cd A-Multimodal-Approach-to-Research-Paper-Summarization
   ```

2. **Setup the virtual environment**

   Create a virtual environment in the project directory (skip this step if you have already created one):

   ```bash
   python -m venv venv
   ```

   Activate the virtual environment:

   ```bash
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix or MacOS
   ```

3. **Install dependencies**

   Install all the required packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

   To ensure all dependencies are captured for other users, update the `requirements.txt` file regularly:  After each change if you install anything please do this step so that packages will get copied to requirements.txt

   ```bash
   pip freeze > requirements.txt
   ```

## Running the Code

```bash
uvicorn app.main:app --reload
```

## pushing code to github

```bash
git add .
git commit -m "meaningful message based on your changes"
git push origin <branch_name>
```


