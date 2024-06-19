# Observability Pipeline Image

This is the home of the docker image used by most if not all the CI pipeline Jobs

## How to build

1. From the project root, execute the following, replacing `<VERSION>` with the new version.

```shell
docker build -f observability/deploy/pipeline/pipeline-container.dockerfile -t datakitchen/dataops-observability-dev-pipeline:<VERSION> .
```

2. Push the image to dockerhub. Also replace `<VERSION>` with the new version.

```shell
docker push datakitchen/dataops-observability-dev-pipeline:<VERSION>
```

3. Update `.gitlab-ci.yaml` to match.