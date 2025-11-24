[![MIT License](https://img.shields.io/github/license/bcgov/quickstart-openshift.svg)](/LICENSE.md)
[![Lifecycle:Dormant](https://img.shields.io/badge/Lifecycle-Dormant-ff7f2a)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)

[![Merge](https://github.com/bcgov/nr-rfc-alertauthoring/actions/workflows/merge.yml/badge.svg)](https://github.com/bcgov/nr-rfc-alertauthoring/actions/workflows/merge.yml)
[![Analysis](https://github.com/bcgov/nr-rfc-alertauthoring/actions/workflows/analysis.yml/badge.svg)](https://github.com/bcgov/nr-rfc-alertauthoring/actions/workflows/analysis.yml)
[![Scheduled](https://github.com/bcgov/nr-rfc-alertauthoring/actions/workflows/scheduled.yml/badge.svg)](https://github.com/bcgov/nr-rfc-alertauthoring/actions/workflows/scheduled.yml)

##### Frontend (JavaScript/TypeScript) - *not connected, to be updated*
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_frontend&metric=bugs)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_frontend)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_frontend&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_frontend)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_frontend&metric=coverage)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_frontend)
[![Duplicated Lines](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_frontend&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_frontend)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_frontend&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_frontend)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_frontend&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_frontend)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_frontend&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_frontend)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_frontend&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_frontend)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_frontend&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_frontend)

##### Backend (JavaScript/TypeScript) - *not connected, to be updated*
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_backend&metric=bugs)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_backend)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_backend&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_backend)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_backend&metric=coverage)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_backend)
[![Duplicated Lines](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_backend&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_backend)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_backend&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_backend)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_backend&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_backend)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_backend&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_backend)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_backend&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_backend)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=quickstart-openshift_backend&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=quickstart-openshift_backend)

# Hydrological Alerting App

<img src="https://lh3.googleusercontent.com/pw/AP1GczMIx4KLo76HzHvqjse6snbO0qFPWrEJJMDFUs6xGEh5DymiT6_c1aKw8rfAlcQ_To7fpE-KyJr2sOItJlrdyAM4GfqyoQw1sMxik45sJoIKnuzlkLAlVNHrkyYs1E-CFyILuHy2-79XsLpSUZ1Efx7-CA=w1607-h723-s-no-gm?authuser=0" width="700px">

A way to define alerts for hydrological advisories.  This application will 
eventually tie in with providing a common alerting protocol feed, which will 
allow interested parties to subscribe, and recieve notifications about the 
status of hydrological conditions in their area.

Project is currently in its early phases of development

## Local Development Configuration

See [local development](./docs/local_dev.md) for guide to setting up a local 
development environment.

## Tech Stack

### Backend

Using Python / [Fastapi](https://fastapi.tiangolo.com/), and the newer sqlmodel for serialization and orm model.
[Backend Readme](backend/README.md)

Using Alembic for database migrations.  See Alembic [docs](docs/db_migration_alembic.md)

[Docs describing the planned flow for the database](docs/backend-planning/data_flow.md)

### Frontend

Using Angular, [Developing Frontend Docs](frontend/hydro_alerting/README.md)

[Frontend Development plan / wireframes](docs/frontend-planning/frontend-wireframes.md)


## Test instance

A test instance of the application can be viewed here:
https://nr-rfc-alertauthoring-test-frontend.apps.silver.devops.gov.bc.ca
