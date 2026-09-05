"""Runtime settings loaded from the environment."""

import os


def region() -> str:
    """Return the deployment region. Production always sets DEPLOY_REGION."""
    return os.environ["DEPLOY_REGION"]


def bucket_name(project: str) -> str:
    return f"{project}-{region()}-assets"
