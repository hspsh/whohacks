import dagger
from dagger import dag, function, object_type


@object_type
class Whohacks:
    @function
    async def build_and_push(
        self,
        *,
        git_ref: str,
        git_commit: str,
        registry: str,
        image_name: str,
        registry_user: str,
        registry_token: dagger.Secret,
    ) -> str:
        ctr = (
            dag.container()
            .build(dag.host().directory("."), dockerfile="docker/web/Dockerfile")
            .with_registry_auth(registry, registry_user, registry_token)
        )

        full_name = f"{registry}/{image_name}"
        await ctr.publish(f"{full_name}:dev-{git_commit}")

        if git_ref == "refs/heads/master":
            await ctr.publish(f"{full_name}:latest")
