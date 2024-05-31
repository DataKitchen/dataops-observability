# type: ignore
# invoke type issue: https://github.com/pyinvoke/invoke/issues/357
__all__ = [
    "build",
    "helm_app",
    "helm_services",
    "helm_build",
    "local",
    "minikube",
    "nuke",
    "restart",
    "update",
    "host_env",
    "host_run",
    "check_required_tools",
]

import functools
import os
import platform
import re
from collections import defaultdict
from dataclasses import dataclass
from inspect import Parameter, Signature
from time import sleep

import yaml
from invoke import Exit, Task, task
from packaging import version

from scripts.invocations.common import MINIKUBE_PROFILE, check_env_tools, get_docker_env, get_host_env

KUBE_VERSION = os.environ.get("INVOKE_KUBE_VERSION", "v1.25.7")
NAMESPACE = "datakitchen"
HELM_SVC_FOLDER = os.path.join("deploy", "charts", "observability-services")
HELM_APP_FOLDER = os.path.join("deploy", "charts", "observability-app")
HELM_APP_VALUES = os.path.join("deploy", "charts_values", "values-app-dev.yaml")
HELM_SVC_VALUES = os.path.join("deploy", "charts_values", "values-services-dev.yaml")

DOCKER_BUILDER_NAME = "dk-builder"
DOCKER_BUILDER_PLATFORMS = "linux/amd64,linux/arm64"


@dataclass
class Module:
    name: str
    run_cmd: str

    @property
    def name_u(self):
        return self.name.replace("-", "_")


class ModuleListTask(Task):
    """
    Extension of `invoke.Task` that adds one boolean argument per module on top of existing arguments. It compiles back
    the input data into a list of `Module` objects.
    """

    # Eg:
    #    MODULES = (
    #        Module("some-api", "uwsgi --ini=some_api/api.ini"),
    #        Module("other-api", "uwsgi --ini=other_api/api.ini"),
    #    )
    # Populate this tuple in subclasses for generating task-list arguments
    MODULES = ()

    def argspec(self, body):
        signature = super().argspec(body)
        params = [v for k, v in signature.parameters.items() if k != "modules"]
        params.extend(Parameter(m.name_u, Parameter.POSITIONAL_OR_KEYWORD, default=False) for m in self.MODULES)
        return Signature(params)

    def __call__(self, *args, **kwargs):
        modules = []
        for mod in self.MODULES:
            if kwargs.pop(mod.name_u, False):
                modules.append(mod)
        kwargs["modules"] = modules

        super().__call__(*args, **kwargs)


class DeployModuleListTask(ModuleListTask):
    MODULES = (
        Module("observability-api", "gunicorn --reload observability_api.app:app"),
        Module("event-api", "gunicorn --reload event_api.app:app"),
        Module("agent-api", "gunicorn --reload agent_api.app:app"),
        Module("observability-ui", "nginx -g daemon off;"),
        Module("run-manager", "run-manager"),
        Module("rules-engine", "rules-engine"),
        Module("scheduler", "scheduler"),
    )


deploy_module_task = functools.partial(task, klass=DeployModuleListTask)
"""Replacement for the `task` decorator that receives a list of deployable modules as argument."""


def _scale_deployment(ctx, module, count, timeout=0):
    return ctx.run(
        f"kubectl --context {MINIKUBE_PROFILE} scale --replicas={count} --timeout={timeout}s deployment/{module.name}"
    )


def _find_keys(data, key):
    """Find `key` in nested dict and lists"""
    if isinstance(data, list):
        for i in data:
            yield from _find_keys(i, key)
    elif isinstance(data, dict):
        if key in data:
            yield data[key]
        for j in data.values():
            yield from _find_keys(j, key)


def _pre_load_images(ctx):
    """
    Load non-app images into minikube machine

    Instead of downloading non-app images for every new minikube profile
    they are cached on the host and loaded into minikube. Observability images are
    not download or cached as they are built anew every time.
    """

    result = ctx.run(_build_helm_command(HELM_SVC_FOLDER, template=True), hide="stdout")
    images = set()
    # Collect all images from helm output
    for data in yaml.safe_load_all(result.stdout):
        for image in _find_keys(data, "image"):
            images.add(image)

    for image in images:
        # --overwrite and --remote enables usage of image host cache
        ctx.run(f"minikube -p {MINIKUBE_PROFILE} image load --overwrite=false --remote=true {image}", echo=True)


@task(name="required-tools")
def check_required_tools(ctx):
    check_env_tools(required_tools=("kubectl", "minikube", "docker", "helm"))


@task(
    pre=(check_required_tools,),
    help={
        "driver": "choose the driver for the new minikube profile",
        "memory": "set available memory in minikube e.g. 7168m",
        "cpus": "set available cores in minikube, a number or 'max'",
    },
)
def minikube(ctx, driver=None, memory=None, cpus=None):
    """
    Start minikube instance

    If the driver is not specified, the instance is started with the docker or hyperkit driver, depending on the OS.
    It is started in a separate profile to not interfere with other instances.

    Environment variables:
        INVOKE_KUBE_VERSION:      Override Kubernetes version
        INVOKE_MINIKUBE_PROFILE:  Override minikube profile
    """

    driver = driver or ("hyperkit" if platform.system() == "Darwin" else "docker")
    memory_arg = "" if memory is None else f"--memory {memory}"
    cpus_arg = "" if cpus is None else f"--cpus {cpus}"

    ctx.run(
        (
            f"minikube start -p {MINIKUBE_PROFILE} "
            f"{memory_arg} "
            f"{cpus_arg} "
            f"--driver={driver} "
            f"--kubernetes-version={KUBE_VERSION} "
            "--embed-certs "
            "--extra-config=apiserver.service-node-port-range=1-65535 "
            "--extra-config=kubelet.allowed-unsafe-sysctls=net.core.somaxconn "
        )
    )
    ctx.run(f"minikube profile {MINIKUBE_PROFILE}")
    ctx.run(f"kubectl config set-context {MINIKUBE_PROFILE} --namespace={NAMESPACE}")
    ctx.run(f"minikube -p {MINIKUBE_PROFILE} status")

    # This is a workaround to enable connections from the minikube machine to host. The workaround is merged to minikube
    # and released with version 1.30.0 [1], although there is still an open issue for it [2].
    # [1] https://github.com/kubernetes/minikube/pull/16207
    # [2] https://github.com/kubernetes/minikube/issues/15573
    match = re.match(r"minikube version: (?P<version>.*)", ctx.run("minikube version", hide=True).stdout, re.M)
    if platform.system() == "Linux" and match and version.parse("1.30.0") > version.parse(match.group("version")):
        # This workaround is taken from https://github.com/kubernetes/minikube/issues/14631#issuecomment-1292420728
        ctx.run(
            """minikube ssh "sudo iptables-save | sed -e '/--dport 53/! s/\(-A DOCKER_OUTPUT .*\)/\\1 --dport 53/' | sudo iptables-restore" """
        )


@task(pre=(check_required_tools,))
def helm_build(ctx):
    """
    Update and build external dependencies (e.g. MySQL, Kafka)

    This is not required when only updating Observability's charts.
    """
    ctx.run("helm repo add bitnami https://charts.bitnami.com/bitnami")
    ctx.run("helm dependency build deploy/charts/observability-services")


def _build_helm_command(
    chart_folder, *extra_args, release=None, upgrade=False, template=False, atomic=False, timeout=None, **extra_values
):
    args = []
    args.extend(extra_args)
    if template:
        cmd = "template"
        args.append(f"--kube-version {KUBE_VERSION}")
        args.append("--debug")
    else:
        cmd = "upgrade" if upgrade else "install"
        args.append(f"--kube-context {MINIKUBE_PROFILE}")
        args.append(f"--namespace {NAMESPACE}")
        if atomic:
            args.append("--atomic")
        else:
            args.append("--wait")
        if timeout:
            args.append(f"--timeout={timeout}")
    if not release:
        release = os.path.split(chart_folder)[-1]
    for k, v in extra_values.items():
        args.append(f"--set={k}={v}")

    return f"helm {cmd} {' '.join(args)} {release} {chart_folder}"


@task(pre=(check_required_tools,))
def helm_app(ctx, upgrade=False, template=False, atomic=False, timeout=None):
    """
    Deploy/Update Observability's cluster using helm chart with development values

    The development values are geared towards a better development experience
    and debugging.  E.g. services are exposed to the host and some have a more
    lenient configuration.
    """
    ctx.run(
        _build_helm_command(
            HELM_APP_FOLDER,
            f"--values {HELM_APP_VALUES}",
            upgrade=upgrade,
            template=template,
            atomic=atomic,
            timeout=timeout,
        )
    )


@task(pre=(check_required_tools,))
def helm_services(ctx, upgrade=False, template=False, atomic=False, timeout=None):
    _pre_load_images(ctx)
    ctx.run(
        _build_helm_command(
            HELM_SVC_FOLDER,
            f"--create-namespace --values {HELM_SVC_VALUES}",
            upgrade=upgrade,
            template=template,
            atomic=atomic,
            timeout=timeout,
        )
    )


# https://github.com/pyinvoke/invoke/issues/378
@task(
    pre=(check_required_tools,),
    help=dict(
        (
            ("tag", "Image tag. Defaults to 'latest'"),
            ("no-cache", "Disables docker layer caching"),
            ("backend", "Builds only the Observability backend image"),
            ("ui", "Builds only the Observability UI image"),
            ("base-image-url", "Base image prefix. Useful to enable a dependency proxy"),
            ("local", "Use the local docker instead of minikube's."),
        )
    ),
)
def build(
    ctx,
    backend=False,
    ui=False,
    tag="latest",
    no_cache=False,
    base_image_url=None,
    local=False,
):
    """
    Build Observability's images inside the minikube instance.

    Builds all images by default.
    """

    # If nothing was chosen, build everything
    if not any((backend, ui)):
        backend = True
        ui = True

    # "minikube image build" support for build-arg is clunky, using the docker CLI instead
    env = {} if local else get_docker_env(ctx)

    args_str = ""
    if no_cache:
        args_str += "--no-cache "
    if base_image_url:
        base_image_url = base_image_url if base_image_url.endswith("/") else f"{base_image_url}/"
        args_str += f"--build-arg BASE_IMAGE_URL={base_image_url} "

    if backend:
        ctx.run(
            f"docker build . {args_str} --build-arg tag={tag} "
            f"-t 'observability-be:{tag}' -f ./deploy/docker/observability-be.dockerfile",
            env=env,
        )

    if ui:
        ctx.run(
            f"docker build . {args_str} " f"-t 'observability-ui:{tag}' -f ./deploy/docker/observability-ui.dockerfile",
            env=env,
        )


@task(
    pre=(check_required_tools,),
    help=dict(
        (
            ("version", "Platform version. Defaults to 'latest'"),
            ("backend", "Builds only the Observability backend image"),
            ("ui", "Builds only the Observability UI image"),
        )
    ),
)
def build_public_images(
    ctx,
    version,
    backend=False,
    ui=False,
    push=False,
    local=False,
):
    """
    Builds and pushes Observability's images using local docker builder.

    Builds all images by default.
    """

    # If nothing was chosen, build everything
    targets = []
    if ui:
        targets.append("ui")
    if backend:
        targets.append("backend")

    if not targets:
        targets = ("ui", "backend")

    if push and local:
        raise Exit("Cannot use --local and --push at the same time.")

    use_cmd = f"docker buildx use {DOCKER_BUILDER_NAME}"
    if not ctx.run(use_cmd, hide=True, warn=True).ok:
        ctx.run(f"docker buildx create --name {DOCKER_BUILDER_NAME} --platform {DOCKER_BUILDER_PLATFORMS}")
        ctx.run(use_cmd)

    extra_args = []
    if push:
        extra_args.append("--push")
    elif local:
        extra_args.extend(("--load", "--set=*.platform=$BUILDPLATFORM"))
    env = {"OBSERVABILITY_VERSION": version}
    for target in targets:
        ctx.run(f"docker buildx bake -f deploy/docker/docker-bake.json {target} {' '.join(extra_args)}", env=env)


# Invoke does not support **kwargs
@deploy_module_task(
    pre=(check_required_tools,), help={m.name: f"Restart {m.name}" for m in DeployModuleListTask.MODULES[:]}
)
def restart(ctx, modules):
    """
    Restart Observability's deployments.

    Restarts all deployments by default.
    """

    if not modules:
        modules = DeployModuleListTask.MODULES[:]
    ctx.run(f"kubectl --context {MINIKUBE_PROFILE} rollout restart deployment {' '.join(m.name for m in modules)}")


@task(pre=(check_required_tools, build))
def update(ctx):
    """
    Build all docker images and deploy helm charts

    This command is useful after switching branch to have an up-to-date
    minikube deployment.
    """
    helm_app(ctx, upgrade=True)


@task(
    pre=(check_required_tools,),
    help={
        "values": "path to values.yaml file to override/add Helm values",
        "driver": "choose the driver for the new minikube profile",
        "memory": "set available memory in minikube e.g. 7168m",
        "cpus": "set available cores in minikube, a number or 'max'",
        "base-image-url": "Base image prefix. Useful to enable a dependency proxy",
    },
)
def local(ctx, values="", driver=None, memory=None, cpus=None, base_image_url=""):
    """
    Setup local development environment

    Tasks include
    * Start minikube instance
    * Build all docker images
    * Deploy Helm chart with development values

    Required tools: docker, helm, minikube
    """
    minikube(ctx, driver=driver, memory=memory, cpus=cpus)
    build(ctx, base_image_url=base_image_url)
    helm_build(ctx)
    helm_services(ctx, timeout="10m")
    helm_app(ctx, timeout="10m")
    ctx.run(f"minikube -p {MINIKUBE_PROFILE} service --namespace {NAMESPACE} list")


@task(pre=(check_required_tools,))
def nuke(ctx):
    """
    Destroy the local development environment

    N.B. This will delete the minikube machine along with all docker images
    inside it.
    """
    ctx.run(f"minikube -p {MINIKUBE_PROFILE} delete")


@task(pre=(check_required_tools,))
def dump_logs(ctx, directory="logs"):
    """
    Dump minikube logs
    """
    print(f"Dumping logs to directory '{directory}'")
    ctx.run(f"mkdir -p {directory}")
    for module in DeployModuleListTask.MODULES:
        print(f"Writing {module.name}")
        ctx.run(
            f"kubectl --context {MINIKUBE_PROFILE} logs --tail=-1 -l app.kubernetes.io/name={module.name} > {directory}/{module.name}.log"
        )


@task
def host_env(ctx, shell=None):
    """
    Print a snippet of variable setting commands to mimic the cluster configuration into the local shell.

    It auto-detects the current shell from the SHELL environment variable

    Usage:
      $ inv host-env | source

    """

    set_cmd_tpl = defaultdict(lambda: "export {var}='{val}'", {"fish": "set -gx {var} '{val}'"})

    if shell is None:
        _, _, shell = os.environ.get("SHELL", "").rpartition("/")

    template = set_cmd_tpl[shell]

    for var, val in get_host_env(ctx).items():
        print(template.format(var=var, val=val))


@deploy_module_task(
    pre=(check_required_tools,),
    help=dict(
        (
            ("restart", "Automatically restart the module when it finishes"),
            ("keep-pod-running", "Prevent the tool from stopping the module running in the cluster"),
            *((d.name, f"Run the {d.name} module") for d in DeployModuleListTask.MODULES),
        )
    ),
)
def host_run(ctx, modules, restart=False, keep_pod_running=False):
    """
    Run a specific module using the host environment. Automatically stops the module running in the cluster.
    """
    if len(modules) != 1:
        raise Exit("Exactly one module should be chosen at a time.", code=1)

    env = get_host_env(ctx)
    mod = modules[0]
    try:
        if not keep_pod_running:
            _scale_deployment(ctx, mod, 0)
        while True:
            ctx.run(mod.run_cmd, env=env)
            if restart:
                try:
                    # These sleeps are meant to give the user some time to break the restart loop.
                    print("\n -> Restarting in", end=" ", flush=True)
                    for i in range(3, 0, -1):
                        print(f"{i}..", end=" ", flush=True)
                        sleep(1)
                    print("\n")
                except KeyboardInterrupt:
                    print("\n")
                    break
            else:
                break
    finally:
        if not keep_pod_running:
            _scale_deployment(ctx, mod, 1)
