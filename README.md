# Labware Tracker: Flask Web Application with Continuous Deployment

This repository hosts the Flask-based web application for tracking labware in a biomedical environment. It leverages **Continuous Deployment (CD)** to deploy the application to a **Google Cloud Platform (GCP)** Virtual Machine (VM) using **Docker** and **GitHub Actions**.

### Steps for Deploying a Google Cloud Platform (GCP) Virtual Machine

This section outlines the **deployment plan** for creating a GCP VM and deploying the Flask application within a CI/CD pipeline.

#### **1. GCP VM Setup Using Terraform (Infrastructure as Code)**

To automate the creation of the GCP VM, I have used **Terraform**, a tool that allows us to define the infrastructure in a configuration file and alter it automatically. Follow the steps below to change the GCP resources:

* Clone the Terraform GCP Compute Instance repository or use the following Terraform script to create the VM on GCP:

```hcl
provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_compute_instance" "labware-instance" {
  name         = "labware-instance"
  machine_type = "e2-medium"
  zone         = var.zone
  boot_disk {
    initialize_params {
      image = "ubuntu-2004-focal-v20210701"
    }
  }
  network_interface {
    network = "default"
    access_config {
      // Ephemeral IP
    }
  }

  metadata_startup_script = <<-EOT
    #! /bin/bash
    sudo apt-get update
    sudo apt-get install docker.io -y
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo docker run -d -p 5000:5000 labware-tracker:latest
  EOT
}

output "instance_ip" {
  value = google_compute_instance.labware-instance.network_interface[0].access_config[0].nat_ip
}
```

* Replace the `var.project_id`, `var.region`, and `var.zone` with your GCP project details.
* Run `terraform apply` to create the instance.

This Terraform script will automatically create a VM and install Docker. It will then run the Flask application in a Docker container, exposing it on port 5000.

#### **2. Deploying the Flask Application on the GCP VM (Using Docker)**

Once the VM is created, we deploy the Flask application using Docker, ensuring that the app runs in an isolated container.

##### Steps:

1. **SSH into the GCP VM**:

   * Connect to the VM through SSH using the following command:

     ```bash
     gcloud compute ssh --project PROJECT_ID --zone ZONE VM_NAME
     ```
   * Alternatively, you can SSH directly from the GCP console.

2. **Clone the GitHub repository** on the VM:

   ```bash
   git clone https://YOUR_GIT_USERNAME:YOUR_GIT_TOKEN@github.com/YOUR_USERNAME/LabwareTracker.git
   cd LabwareTracker
   ```

3. **Build the Docker image** for the Flask app:

   ```bash
   docker build -t labware-tracker .
   ```

4. **Run the Docker container** on the VM, exposing the application on port 5000:

   ```bash
   docker run -d -p 5000:5000 labware-tracker
   ```

#### **3. CI/CD Pipeline with GitHub Actions**

Once the application is working on the VM, we use GitHub Actions to automate the deployment process every time changes are pushed to the `main` branch. This is accomplished by the following workflow:

1. **Set up the Workflow**:

   * Navigate to the **Actions** tab of this GitHub repository.
   * Enable the **workflow** for **continuous deployment**.

2. **Configure Secrets for GCP Authentication**:

   * Encode your **Terraform Service Account** credentials (in JSON format) as a **BASE64** string.
   * Add this as a GitHub secret named `GCP_TF_SA_CREDS_BASE64`.

3. **Create a `build_and_deploy.yaml` file** inside the `.github/workflows` directory:

   ```yaml
   name: Setup, Build, Deploy and Publish

   on:
     push:
       branches:
         - 'main'
     release:
       types: [created]

   jobs:
     setup-build-deploy-publish:
       name: Setup, Build, Deploy and Publish
       runs-on: ubuntu-latest

       environment: production
       env:
         PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
         GCP_ZONE: ${{ secrets.GCP_ZONE }}
         INSTANCE_NAME: ${{ secrets.INSTANCE_NAME }}
         IMAGE_NAME: labware-tracker
         CONTAINER_NAME: labware-container
         REPO_URL: ${{ secrets.REPO_URL }}
       
       steps:
         - name: Checkout repository
           uses: actions/checkout@v2

         - name: Set up Docker
           uses: docker/setup-buildx-action@v1

         - name: Build Docker image
           run: |
             docker build -t ${{ env.IMAGE_NAME }} .

         - name: Log in to GCP
           uses: google-github-actions/auth@v0
           with:
             credentials_json: ${{ secrets.GCP_TF_SA_CREDS_BASE64 }}

         - name: Push Docker image to Google Container Registry
           run: |
             docker tag ${{ env.IMAGE_NAME }} gcr.io/${{ secrets.GCP_PROJECT_ID }}/${{ env.IMAGE_NAME }}
             docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/${{ env.IMAGE_NAME }}

         - name: Deploy to GCP VM
           run: |
             gcloud compute ssh --zone ${{ env.GCP_ZONE }} ${{ env.INSTANCE_NAME }} --command "docker pull gcr.io/${{ secrets.GCP_PROJECT_ID }}/${{ env.IMAGE_NAME }} && docker run -d -p 5000:5000 gcr.io/${{ secrets.GCP_PROJECT_ID }}/${{ env.IMAGE_NAME }}"
   ```

4. **Push changes** to GitHub:
   Every time you push changes to the `main` branch, GitHub Actions will automatically:

   * Build the Docker image
   * Push it to Google Container Registry
   * SSH into the GCP VM
   * Pull the latest image and restart the container with the new code.

#### **4. Continuous Deployment Monitoring**

You can monitor the progress of the deployment and the state of the virtual machine through the **GitHub Actions** tab and GCP's **Compute Engine** dashboard. Any issues or failures in the pipeline will be visible in the Actions logs.

---

### Additional Notes:

* If you prefer to manually set up the VM, skip the Terraform steps and follow the manual SSH and Docker steps instead.
* This workflow ensures that changes to the codebase are automatically deployed without manual intervention, streamlining the deployment process for continuous integration and continuous delivery (CI/CD).

