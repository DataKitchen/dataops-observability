# DataOps Observability Docker Compose

## Overview

This document describes how to use Docker Compose to deploy Observability. The provided compose
file can be used without modifications to deploy to a local, trial docker environment, or can
be modified to guide a cloud-based deployment.

> [!IMPORTANT]
> For your convenience, the provided compose file has the services (database and message broker)
> connectivity configuration at their most simplistic form, which is not secure for a production deployment.

## Local deployment

The following command will start the platform, using its default configurations. All the commands
mentioned in this document assumes Docker is installed and the `compose.yaml` and `config.env` files are within the
current folder

```shell
docker compose up -d
```

When the command returns successfully, it means that the platform in running in the background, and you can proceed to
seeding the minimal data it needs, which includes creating a user account. The following command will prompt you
for the user account information.

```shell
docker compose run --rm -it observability_data_init init --data
```

Once that is finished, you can access the platform using the credentials you created at http://localhost:8082/

The data initialization also provides some information that you must have available if you are planning to
interact with the platform using its integration APIs. Store this information somewhere, if that is the case. This
is an example of what this information will look like:

```
INFO:               company_id: 6a6e5aa0-76cb-45d9-b1f5-cad3ebaf1cb4
INFO:          organization_id: 6cfa3063-5220-4061-8004-df5b32cd54a2
INFO:               project_id: b85ebf07-fa4f-4cc8-9362-d78ec800e2c0
INFO:                  user_id: f5c30e55-d2e2-4b1f-baec-9901f56060e0
```

Your DataOps Observability platform is deployed and ready.

Once you are done, you can stop the platform without losing your data, by issuing the command below. You
can start and stop it at any time.

```shell
docker compose down
```

## Configurations

The Docker Compose file allows you to configure certain aspects of the deployment. The `config.env` file serves as a
reference of which environment variables are considered, and can be edited as needed. In that case, most of the
"docker compose" commands will need an argument pointing to this file to be included, as the example below.

```shell
docker compose --env-file=conig.env up -d
```

## Upgrading

Upgrading Observability to its latest version only requires the new images to be pulled, and starting fresh containers
running the updated images. The following command pulls the images. Note the `--policy=always` argument. It forces
pulling even when the images are already present.

```shell
docker compose pull --policy=always
```

Next, you will need to restart the application containers, which can be achieved with the same installation command.
The database migrations, if any, will automatically run during the restart. It can be executed whether the
application is running or not.

```
docker compose up -d
```
