# GCP Continuous Deployment for Labware Flask API

This repository contains a simple Flask web application demonstrating the Continuous Deployment (CD) pipeline on Google Cloud Platform (GCP) Compute Engine instances using Docker and GitHub workflows.

## Prerequisites

Before starting, ensure that the following are configured in your Google Cloud Platform (GCP) environment:

1. **GCP Instance and VPC Network**:

   * The GCP instance should allow HTTP(S) traffic on port 5000 to expose the container and enable SSH access using the `gcloud compute ssh` command.
   * You can either create a VM instance manually or use this [Terraform repository](https://github.com/warestack/terraform-gcp-compute-instance) to provision the necessary resources.

2. **Google Cloud Project**:

   * Ensure your GCP project is set up and the Compute Engine API is enabled.

## Setting Up Your Local Development Environment

### 1. Create a Simple Flask Application

Create a Python script `app.py` with the following code to implement a basic Flask API for managing labware data:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory data store for labware info
labware_data = {}

@app.route('/labware', methods=['GET'])
def get_labware():
    # Returns the labware information
    return jsonify(labware_data), 200

@app.route('/labware', methods=['POST'])
def add_labware():
    # Gets the data sent in the POST request
    new_labware = request.get_json()

    # Validate labware name and type
    if not new_labware.get('name') or not new_labware.get('type'):
        return jsonify({'error': 'Missing labware name or type'}), 400

    # Add the new labware to the data store
    labware_id = len(labware_data) + 1  # Generate ID based on current length
    labware_data[labware_id] = new_labware

    return jsonify({'message': 'Labware added successfully', 'id': labware_id}), 201

if __name__ == '__main__':
    app.run(debug=True)
```

This Flask application provides two endpoints:

* `GET /labware` to retrieve the labware information.
* `POST /labware` to add new labware data.

### 2. Install Flask

Ensure Flask is installed on your local machine by running:

```bash
pip install flask
```

You can then run the application:

```bash
python3 app.py
```

### 3. Initialize a Git Repository

Set up version control using Git by following these steps:

1. **Initialize Git** in your project folder:

   ```bash
   git init
   ```

2. **Add a remote repository** (replace `YOUR_GIT_USERNAME` and `YOUR_GIT_REPO` with your actual GitHub username and repository):

   ```bash
   git remote add origin https://YOUR_GIT_USERNAME:YOUR_GIT_TOKEN@YOUR_GIT_REPO
   ```

3. **Add and commit the files**:

   ```bash
   git add .
   git commit -m "Initial commit - Flask app"
   ```

4. **Push the code** to GitHub:

   ```bash
   git push -f origin main
   ```

After pushing, you should be able to see your files in the GitHub repository.

## Deploying the Flask Application on GCP VM (Manually)

### 1. Connect to Your GCP VM

SSH into your GCP VM instance. You can use either the terminal or the "SSH" button on the Google Cloud Console.

### 2. Clone Your GitHub Repository

Clone the repository containing the Flask application to your GCP VM:

```bash
git clone --branch main https://YOUR_GIT_USERNAME:YOUR_GIT_TOKEN@YOUR_GIT_REPO
```

### 3. Build the Docker Image

Navigate to your cloned repository and create a Docker image for the Flask app:

```bash
cd flask-app
docker build -t flask .
```

### 4. Run the Flask App in a Docker Container

Run the Docker container on your VM and expose port 5000:

```bash
docker run -d -p 5000:5000 flask
```

You can now access the Flask application by navigating to `http://<VM_PUBLIC_IP>:5000`.

## Continuous Deployment with GitHub Workflow

To automate the deployment of your Flask application using GitHub Actions, follow these steps:

### 1. Set Up GitHub Workflow

Enable GitHub Actions in your repository. Navigate to the **Actions** tab and enable the workflow.

### 2. Store Google Cloud Credentials

Encode your Terraform service account JSON file in `BASE64` format and store it as a secret in GitHub, named `GCP_TF_SA_CREDS_BASE64`.

### 3. Configure the GitHub Workflow

Create a `build_and_deploy.yaml` file in `.github/workflows/`. The file will automate the deployment process. Here’s an example:

```yaml
name: Build and Deploy to GCP

on:
  push:
    branches:
      - main
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    env:
      PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
      GCP_ZONE: ${{ secrets.GCP_ZONE }}
      INSTANCE_NAME: ${{ secrets.INSTANCE_NAME }}
      REPO_URL: ${{ secrets.REPO_URL }}

    steps:
    - name: Checkout repository
      uses: actions/checkout@v2

    - name: Set up Google Cloud credentials
      uses: google-github-actions/setup-gcloud@v0.2.0
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        credentials_json: ${{ secrets.GCP_CREDENTIALS_JSON }}

    - name: SSH into VM and deploy
      run: |
        gcloud compute ssh ${{ secrets.INSTANCE_NAME }} --zone ${{ secrets.GCP_ZONE }} --command="cd /path/to/app && git pull && docker-compose up -d"
```

### 4. Monitor the Deployment

After pushing changes to the main branch, the workflow will automatically trigger. You can monitor the progress of the deployment in the GitHub Actions tab.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

---

Let me know if you need further adjustments!
