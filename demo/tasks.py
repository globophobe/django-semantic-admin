import os

from invoke import run, task


@task
def django_settings(ctx):
    os.environ["DJANGO_SETTINGS_MODULE"] = "demo.settings.development"
    import django

    django.setup()
    from django.conf import settings

    return settings


@task
def build(ctx):
    delete_database(ctx)
    delete_media(ctx)
    delete_migrations(ctx)
    create_database(ctx)
    create_user(ctx)
    populate_database(ctx)


@task
def create_database(ctx):
    run("python manage.py makemigrations")
    run("python manage.py migrate")


@task
def create_user(ctx):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create(username="demo", is_superuser=True, is_staff=True)
    user.set_password("demo")
    user.save()


@task
def populate_database(ctx):
    django_settings(ctx)

    import datetime
    import os
    import random

    from django.conf import settings
    from django.core.files import File
    from django.utils.text import slugify
    from faker import Faker

    from demo_app.factory import PersonFactory
    from demo_app.models import Favorite, Picture

    fake = Faker()

    COFFEE_DIR = settings.BASE_DIR / "coffee"

    coffees = [c for c in os.listdir(COFFEE_DIR) if os.path.splitext(c)[1] == ".jpeg"]

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
        total_friends = int(random.random() * 5)
        can_be_friends = [p for p in people if person != p]
        friends = random.sample(can_be_friends, total_friends)
        person.friends.add(*friends)

    pictures = []
    random.shuffle(coffees)
    for coffee in coffees:
        path = COFFEE_DIR / coffee
        coffee_person = random.choice(people)
        with open(path, "rb") as f:
            date_and_time = fake.past_datetime().replace(tzinfo=datetime.timezone.utc)
            picture = Picture(person=coffee_person, date_and_time=date_and_time)
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
def delete_database(ctx):
    django_settings(ctx)

    from django.conf import settings

    db = settings.BASE_DIR / "db.sqlite3"
    if db.exists():
        run(f"rm {db}")


@task
def delete_media(ctx):
    django_settings(ctx)

    from django.conf import settings

    if settings.MEDIA_ROOT.exists():
        run(f"rm -r {settings.MEDIA_ROOT}")


@task
def delete_migrations(ctx):
    import os

    from django.conf import settings

    MIGRATIONS_DIR = settings.BASE_DIR / "demo_app/migrations/"

    migrations = [
        MIGRATIONS_DIR / migration
        for migration in os.listdir(MIGRATIONS_DIR)
        if os.path.splitext(migration)[0] != "__init__"
        and os.path.splitext(migration)[1] == ".py"
    ]

    for migration in migrations:
        run(f"rm {migration}")


@task
def push_container(ctx, hostname="asia.gcr.io"):
    django_settings(ctx)
    from django.conf import settings

    project_id = run("gcloud config get-value project").stdout.strip()
    name = f"{hostname}/{project_id}/django-semantic-admin"
    # Requirements
    requirements = [
        "gunicorn",
        "django-filter",
        "django-taggit",
        "pillow",
        "whitenoise",
    ]
    # Versions
    reqs = "\\ ".join(
        [
            req
            for req in run("poetry export --dev --without-hashes").stdout.split("\n")
            if req.split("==")[0] in requirements
        ]
    )
    # Build
    build_args = (
        f"--build-arg POETRY_EXPORT={reqs} "
        f"--build-arg SECRET_KEY='{settings.SECRET_KEY}'"
    )
    cmd = f"docker build {build_args} --file=Dockerfile --tag={name} ."
    ctx.run(cmd)
    import pdb

    pdb.set_trace()
    # Push
    cmd = f"docker push {name}"
    ctx.run(cmd)
