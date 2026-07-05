from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectConfig:
    name: str
    version: str = "0.1.0"
    extras: str = ""


@dataclass
class CIConfig:
    python_versions: list[str] = field(default_factory=lambda: ["3.12"])
    runner: str = "ubuntu-latest"
    lint: bool = True
    type_check: bool = True


@dataclass
class ReleaseConfig:
    branch: str = "main"
    tag_prefix: str = "v"
    changelog: str = "CHANGELOG.md"


@dataclass
class PyPIConfig:
    enabled: bool = True
    environment: str = "pypi"
    trusted_publishing: bool = True


@dataclass
class DebianConfig:
    enabled: bool = True
    email: str = ""
    name: str = ""
    owner: str = ""
    ppa: str = "tools"
    distributions: list[str] = field(default_factory=lambda: ["noble"])
    revision: str = "1"


@dataclass
class GitHubConfig:
    ci: bool = True
    release: bool = True
    publish_pypi: bool = True
    publish_launchpad: bool = True


@dataclass
class DockerConfig:
    enabled: bool = False
    base_image: str = "3.12"
    port: int = 8000
    volumes: list[str] = field(default_factory=list)


@dataclass
class DeployConfig:
    enabled: bool = False
    fly: bool = True
    heroku: bool = True
    railway: bool = True
    primary_region: str = "iad"
    port: int = 8000
    memory: str = "512mb"
    cpu_kind: str = "shared"
    cpus: int = 1


@dataclass
class PyGenesisConfig:
    project: ProjectConfig
    ci: CIConfig = field(default_factory=CIConfig)
    release: ReleaseConfig = field(default_factory=ReleaseConfig)
    pypi: PyPIConfig = field(default_factory=PyPIConfig)
    debian: DebianConfig = field(default_factory=DebianConfig)
    github: GitHubConfig = field(default_factory=GitHubConfig)
    docker: DockerConfig = field(default_factory=DockerConfig)
    deploy: DeployConfig = field(default_factory=DeployConfig)

    @classmethod
    def load(cls, path: str | Path) -> PyGenesisConfig:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")

        raw = path.read_bytes()
        data = tomllib.loads(raw.decode("utf-8"))

        return cls(
            project=ProjectConfig(
                name=data.get("project", {}).get("name", ""),
                version=data.get("project", {}).get("version", "0.1.0"),
                extras=data.get("project", {}).get("extras", ""),
            ),
            ci=CIConfig(
                python_versions=data.get("ci", {}).get("python_versions", ["3.12"]),
                runner=data.get("ci", {}).get("runner", "ubuntu-latest"),
                lint=data.get("ci", {}).get("lint", True),
                type_check=data.get("ci", {}).get("type_check", True),
            ),
            release=ReleaseConfig(
                branch=data.get("release", {}).get("branch", "main"),
                tag_prefix=data.get("release", {}).get("tag_prefix", "v"),
                changelog=data.get("release", {}).get("changelog", "CHANGELOG.md"),
            ),
            pypi=PyPIConfig(
                enabled=data.get("pypi", {}).get("enabled", True),
                environment=data.get("pypi", {}).get("environment", "pypi"),
                trusted_publishing=data.get("pypi", {}).get("trusted_publishing", True),
            ),
            debian=DebianConfig(
                enabled=data.get("debian", {}).get("enabled", True),
                email=data.get("debian", {}).get("email", ""),
                name=data.get("debian", {}).get("name", ""),
                owner=data.get("debian", {}).get("owner", ""),
                ppa=data.get("debian", {}).get("ppa", "tools"),
                distributions=data.get("debian", {}).get("distributions", ["noble"]),
                revision=data.get("debian", {}).get("revision", "1"),
            ),
            github=GitHubConfig(
                ci=data.get("github", {}).get("ci", True),
                release=data.get("github", {}).get("release", True),
                publish_pypi=data.get("github", {}).get("publish_pypi", True),
                publish_launchpad=data.get("github", {}).get("publish_launchpad", True),
            ),
            docker=DockerConfig(
                enabled=data.get("docker", {}).get("enabled", False),
                base_image=data.get("docker", {}).get("base_image", "3.12"),
                port=data.get("docker", {}).get("port", 8000),
                volumes=data.get("docker", {}).get("volumes", []),
            ),
            deploy=DeployConfig(
                enabled=data.get("deploy", {}).get("enabled", False),
                fly=data.get("deploy", {}).get("fly", True),
                heroku=data.get("deploy", {}).get("heroku", True),
                railway=data.get("deploy", {}).get("railway", True),
                primary_region=data.get("deploy", {}).get("primary_region", "iad"),
                port=data.get("deploy", {}).get("port", 8000),
                memory=data.get("deploy", {}).get("memory", "512mb"),
                cpu_kind=data.get("deploy", {}).get("cpu_kind", "shared"),
                cpus=data.get("deploy", {}).get("cpus", 1),
            ),
        )

    @classmethod
    def generate_default(cls, name: str) -> str:
        return f"""[project]
name = "{name}"
version = "0.1.0"
extras = ""

[ci]
python_versions = ["3.12", "3.13"]
runner = "ubuntu-latest"
lint = true
type_check = true

[release]
branch = "main"
tag_prefix = "v"
changelog = "CHANGELOG.md"

[pypi]
enabled = true
environment = "pypi"
trusted_publishing = true

[debian]
enabled = true
email = ""
name = ""
owner = ""
ppa = "tools"
distributions = ["noble"]
revision = "1"

[github]
ci = true
release = true
publish_pypi = true
publish_launchpad = true

[docker]
enabled = false
base_image = "3.12"
port = 8000
volumes = []

[deploy]
enabled = false
fly = true
heroku = true
railway = true
primary_region = "iad"
port = 8000
memory = "512mb"
cpu_kind = "shared"
cpus = 1
"""

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.write_text(self._to_toml(), encoding="utf-8")

    def _to_toml(self) -> str:
        return f"""[project]
name = "{self.project.name}"
version = "{self.project.version}"
extras = "{self.project.extras}"

[ci]
python_versions = {self.ci.python_versions}
runner = "{self.ci.runner}"
lint = {str(self.ci.lint).lower()}
type_check = {str(self.ci.type_check).lower()}

[release]
branch = "{self.release.branch}"
tag_prefix = "{self.release.tag_prefix}"
changelog = "{self.release.changelog}"

[pypi]
enabled = {str(self.pypi.enabled).lower()}
environment = "{self.pypi.environment}"
trusted_publishing = {str(self.pypi.trusted_publishing).lower()}

[debian]
enabled = {str(self.debian.enabled).lower()}
email = "{self.debian.email}"
name = "{self.debian.name}"
owner = "{self.debian.owner}"
ppa = "{self.debian.ppa}"
distributions = {self.debian.distributions}
revision = "{self.debian.revision}"

[github]
ci = {str(self.github.ci).lower()}
release = {str(self.github.release).lower()}
publish_pypi = {str(self.github.publish_pypi).lower()}
publish_launchpad = {str(self.github.publish_launchpad).lower()}

[docker]
enabled = {str(self.docker.enabled).lower()}
base_image = "{self.docker.base_image}"
port = {self.docker.port}
volumes = {self.docker.volumes}

[deploy]
enabled = {str(self.deploy.enabled).lower()}
fly = {str(self.deploy.fly).lower()}
heroku = {str(self.deploy.heroku).lower()}
railway = {str(self.deploy.railway).lower()}
primary_region = "{self.deploy.primary_region}"
port = {self.deploy.port}
memory = "{self.deploy.memory}"
cpu_kind = "{self.deploy.cpu_kind}"
cpus = {self.deploy.cpus}
"""
