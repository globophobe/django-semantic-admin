import os
import re
from pathlib import Path
from typing import Any

from decouple import config
from invoke import task


@task
def django_settings(ctx: Any) -> Any:
    """Get django settings."""
    os.environ["DJANGO_SETTINGS_MODULE"] = "demo.settings.development"
    import django

    django.setup()
    from django.conf import settings

    return settings


@task
def build(ctx: Any) -> None:
    """Build the project."""
    delete_database(ctx)
    delete_media(ctx)
    delete_migrations(ctx)
    create_database(ctx)
    create_user(ctx)
    populate_database(ctx)


@task
def create_database(ctx: Any) -> None:
    """Create the database."""
    ctx.run("python manage.py makemigrations")
    ctx.run("python manage.py migrate")


@task
def create_user(ctx: Any) -> None:
    """Create a superuser."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create(username="admin", is_superuser=True, is_staff=True)
    user.set_password("semantic")
    user.save()


@task
def populate_database(ctx: Any) -> None:
    """Populate the database."""
    django_settings(ctx)

    import datetime
    import os
    import random

    from demo_app.factory import PersonFactory
    from demo_app.models import Favorite, Picture
    from django.conf import settings
    from django.core.files import File
    from django.utils.text import slugify
    from faker import Faker

    fake = Faker()

    COFFEE_DIR = settings.BASE_DIR / "coffee"

    coffees = [c for c in os.listdir(COFFEE_DIR) if Path(c).suffix == ".jpeg"]

    people = []
    for index in range(int(len(coffees) / 2)):
        first_name = fake.first_name()
        last_name = fake.first_name()
        name = f"{first_name} {last_name}"
        slug = slugify(name)
        domain = fake.safe_domain_name()
        dotted_name = slug.replace("-", ".")
        email = f"{dotted_name}@{domain}"
        person = PersonFactory(name=name, slug=slug, url=domain, email=email)
        people.append(person)

    for person in people:
        total_friends = int(random.random() * 3)
        can_be_friends = [p for p in people if person != p]
        friends = random.sample(can_be_friends, total_friends)
        person.friends.add(*friends)

    pictures = []
    random.shuffle(coffees)
    coffee_people = people + random.choices(people, k=len(coffees) - len(people))
    for coffee, coffee_person in zip(coffees, coffee_people):
        date_and_time = fake.past_datetime().replace(tzinfo=datetime.timezone.utc)
        picture = Picture(person=coffee_person, date_and_time=date_and_time)
        path = COFFEE_DIR / coffee
        with open(path, "rb") as f:
            picture.picture.save(coffee, File(f))
        tags = fake.bs().split(" ")
        picture.tags.add(*tags)
        pictures.append(picture)

    for person in people:
        total_favorites = 1 + int(random.random() * 5)
        for index in range(total_favorites):
            picture = random.choice(pictures)
            Favorite.objects.get_or_create(person=person, picture=picture)


@task
def delete_database(ctx: any) -> None:
    """Delete the database."""
    django_settings(ctx)

    from django.conf import settings

    db = settings.BASE_DIR / "db.sqlite3"
    if db.exists():
        ctx.run(f"rm {db}")


@task
def delete_media(ctx: Any) -> None:
    """Delete media."""
    django_settings(ctx)

    from django.conf import settings

    if settings.MEDIA_ROOT.exists():
        ctx.run(f"rm -r {settings.MEDIA_ROOT}")


@task
def delete_migrations(ctx: Any) -> None:
    """Delete migrations."""
    import os

    from django.conf import settings

    MIGRATIONS_DIR = settings.BASE_DIR / "demo_app/migrations/"

    migrations = [
        MIGRATIONS_DIR / migration
        for migration in os.listdir(MIGRATIONS_DIR)
        if Path(migration).stem != "__init__" and Path(migration).suffix == ".py"
    ]

    for migration in migrations:
        ctx.run(f"rm {migration}")


@task
def get_container_name(ctx: Any, region: str = "asia-northeast1") -> str:
    """Get container name."""
    project_id = ctx.run("gcloud config get-value project").stdout.strip()
    name = "django-semantic-admin"
    return f"{region}-docker.pkg.dev/{project_id}/{name}/{name}"


def docker_secrets() -> str:
    """Get docker secrets."""
    build_args = [
        f'{secret}="{config(secret)}"' for secret in ("SECRET_KEY", "SENTRY_DSN")
    ]
    return " ".join([f"--build-arg {build_arg}" for build_arg in build_args])


def build_semantic_admin(ctx: Any) -> str:
    """Build semantic admin."""
    result = ctx.run("poetry build").stdout
    return re.search(r"django_semantic_admin-.*\.whl", result).group()


@task
def build_container(ctx: Any, region: str = "asia-northeast1") -> None:
    """Build container."""
    wheel = build_semantic_admin(ctx)
    ctx.run("echo yes | python manage.py collectstatic")
    name = get_container_name(ctx, region=region)
    # Requirements
    requirements = [
        "django-filter",
        "django-taggit",
        "gunicorn",
        "pillow",
        "python-decouple",
        "whitenoise",
    ]
    # Versions
    reqs = " ".join(
        [
            req.split(";")[0]
            for req in ctx.run("poetry export --dev --without-hashes").stdout.split(
                "\n"
            )
            if req.split("==")[0] in requirements
        ]
    )
    # Build
    build_args = {"WHEEL": wheel, "POETRY_EXPORT": reqs}
    build_args = " ".join(
        [f'--build-arg {key}="{value}"' for key, value in build_args.items()]
    )
    with ctx.cd(".."):
        cmd = " ".join(
            [
                "docker build",
                build_args,
                docker_secrets(),
                f"--no-cache --file=Dockerfile --tag={name} .",
            ]
        )
        ctx.run(cmd)


@task
def push_container(ctx: Any, region: str = "asia-northeast1") -> None:
    """Push container."""
    name = get_container_name(ctx, region=region)
    # Push
    cmd = f"docker push {name}"
    ctx.run(cmd)
