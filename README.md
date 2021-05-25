#### Template Project for Discover Platform

This project provides the files and folder structure needed to develop apps that are ready for deployment to Dovel's Discover platform.

Discover users can select and run data modeling and complex scripts
in the cloud with all the resources provisioned for them dynamically.
 

##### Input Folder
* Put input files for local testing in the `/input` folder 
* Discover jobs move input files from AWS S3 into this folder

##### Output Folder
* Put output files in the `/output` folder
* Discover jobs move output files to AWS S3 bucket
* The `results.json` file provides display instructions for Discover UI

##### Application Folder
* `Data Folder` - Put data files used by your program into `data` folder
* `requirements.txt`
* `main.py` - A sample python script
* `autodocker.yml` - auto-docker configuration file

#### Create a conda environment

````
    conda create --name templ python=3.8
    conda activate templ
    pip install  -r requirements.txt
````

### Build and run main.py
* Create a python virtual environment and issue:
```
pip install -r requirements.txt 
```
As you add additional libraries, update the requirements file
```
pip freeze > requirements.txt 
```
* On github, create a new project using this template. For example, `discover-app-1`
* Update main.py to add your own modifications. 
* Note: The sample main.py provides a basic template that reads sample input files with a list of ICD-10 diagnosis codes,
using a data file in the `data` directory, it looks up the definition and generate corresponding output files in output directory.
The sample file also generates a `results.json` file needed by Discover UI.  

* Update `autodocker.yml` file as needed. This file is used by the auto-docker project
to dynamically generate a container and deploy it to AWS ECR.

### Auto-docker 

Auto-docker builds a container image and pushes the result to AWS ECR.

From the command line, checkout the latest code for this project and use auto-docker project to automate
the docker image build and deployment:

```
    cd ~/github      # Your local git project directory 
    git clone https://github.com/DovelLabs/<discover-app-1>
    
    cd discover-app-1
    # If building a container from a branch other than master
    # git checkout your-branch   
    
    cd ..
    git clone https://github.com/DovelLabs/auto-docker
    cd auto-docker

    # The false means do not push to AWS, leave it blank to push to AWS ECR
    python main.py <discover-app-1> ../<discover-app-1>/app {1.0|latest} {true|false} 
    
    # To run on your local docker, issue the following docker command
    # docker run 461136979341.dkr.ecr.us-east-1.amazonaws.com/<discover-app-1>
```
