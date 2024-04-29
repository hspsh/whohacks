import os
import sys

import anyio
import dagger
from dagger import dag


async def build(
    *, git_ref: str, registry: str, image_name: str, registry_user: str, registry_token: str
):
    async with dagger.connection(dagger.Config(log_output=sys.stderr)):
        ctr = (
            dag.container()
            .build(dag.host().directory("."), dockerfile="docker/web/Dockerfile")
            .with_registry_auth(registry, registry_user, registry_token)
        )

        full_name = f"{registry}/{image_name}"

        if git_ref == "refs/heads/main":
            await ctr.publish(f"{full_name}:latest")

        await ctr.publish(f"{full_name}:{git_ref}")

async def run():
    await build(
        git_ref=os.environ["GITHUB_REF"],
        registry="ghcr.io",
        image_name="hspsh/whohacks",
        registry_user=os.environ["GITHUB_ACTOR"],
        registry_token=os.environ["GITHUB_TOKEN"],
    )


if __name__ == "__main__":
    anyio.run(run)
