## Name
BKWire

## Description
This project is designed to pull bankruptcy data sets in the form of PDF, extract, parse and save this dataset into a relational database. The PDF's are downloaded once and stored in S3 for future reference and use by the end-user. The dataset is then cached using REDIS and made available using a Flask API.
## Features
- Scrape PACER
- Download Corporate Bankruptcy Filings(PDF)
- Extract, Parse, Save and Cache - Text from images(Textract)
- Provides a simple API endpoint to access the necessary data elements for the Application

## Visuals
Visual reference can be located at https://busbk.com, along with the associated wireframes and mockups upon request

## Mirco Services
1337ITS leverages the container strategy for all services to date. In the root of the repo is a directroy `docker` which houses all micro services that make up the BKWire application. Each container is built and stored in the private registry and deployed using docker-compose file found at the root of the repository. Adding a service under the `docker` folder and/or editing files nested under `docker` trigger container builds and pushes to the registry.

Once a new docker service is added, edit the docker-compose file to guide the deployment of the new service. This will generate a new "stack" within portainer keeping all micros services tied together for the application.

## API Installation for local use only
To get started with this project locally, you will need the ability to run Docker containers. https://www.docker.com/get-started
Additionally, you will need username and token for private registry authentication(Blake will supply those upon request)
1. Clone this repo
1. Navigate to the root of the project
1. Login to Gitlab private container registry
```
docker login registry.gitlab.com
```
1. create environment-vars.env
```
Get these values from cbford@1337itsolutions.com
```
1. run the following command
```
docker-compose up
```
The above command will run the `docker-compose.yml` file along with `docker-compose.override.yml` allowing you to customize the local development environments as needed.

## Environment
DEV - https://bkwire.1337itsolutions.com
DEV API - https://flask-api.1337itsolutions.com/apidocs


STG - https://stg.bkwire.com
STG API - https://stg-api.bkwire.com/apidocs


PRD - https://bkwire.com
PRD API - https://api.bkwire.com/apidocs



## Secrets
Reach out to cbford@1337itsolutions.com for values

## Environment vars
Environment vars can be placed in the devops/{env} folder - each folder maps to an environment and will get added to the container at run time. You can append to the current vars.env or create a separate file, the deploy script will pick up any files ending in: `.env`

## Branching Strategy
1337ITS Uses a promotion strategy to ensure the same code is ran across all environments. Feature branches should be merged into `development`, from there `development` gets merged into `staging` and staging merged into `production`.  Each merge will trigger a build and deploy respective to the environment/branch the commit/merge was applied.

We use protected branches to prevent divergent branches and only allow commits to `feature` and/or `development`. From there promotion is only allowed through merge requests.

## Deployments
Deployments are done through a custom python script rolled into a container(`micro service`). This allows for full customized deployments onto the Docker Swarm cluster. This method provides the ability for 0 downtime deployments as services are deployed across a fleet of nodes, ensuring the new service comes up clean before retiring the previous version. These nodes are environment based reducing the blast radius in the event of failure or issue with the deployment.

Deploys will be based on `docker-compose.{ENV}.yml` allowing for stack customization across environments respectively.

## Support
Please reach out to Blake Ford for any infrastructure, API and automation requirements. cbford@1337itsolutions.com or on SLACK - `proj-bcw`

## Roadmap
-Create TOML project file for more customization

-Update gehry service with python `click`

## Authors and acknowledgment
[C. Blake Ford](https://www.linkedin.com/in/blake-ford-1337its/)

## License
GNU General Public License (GPL)

## Project status
Currently in development
