from django import template
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import resolve, reverse

register = template.Library()


def get_semantic_app_list(app_list, current_app):
    semantic_app_list = getattr(settings, "SEMANTIC_APP_LIST", None)
    if semantic_app_list:
        apps = []
        for semantic_app in semantic_app_list:
            for app in app_list:
                semantic_app_label = semantic_app.get("app_label", None)
                is_semantic_app = (
                    isinstance(semantic_app_label, str)
                    and semantic_app_label == app["app_label"]
                )
                if is_semantic_app:
                    app["is_active"] = app["app_label"] == current_app
                    semantic_models = semantic_app.get("models", None)
                    if isinstance(semantic_models, list):
                        models = []
                        for semantic_model in semantic_models:
                            semantic_object_name = semantic_model.get(
                                "object_name", None
                            )
                            if isinstance(semantic_object_name, str):
                                for model in app["models"]:
                                    if semantic_object_name == model["object_name"]:
                                        models.append(model)
                        app["models"] = models
                    apps.append(app)
        has_active = any([app["is_active"] for app in apps])
        if len(apps) and not has_active:
            apps[0]["is_active"] = True
        return apps
    else:
        return app_list


def get_app_label(resolver_match):
    if "app_label" in resolver_match.kwargs:
        return resolver_match.kwargs.get("app_label")
    else:
        # Reconstruct from url_name.
        url_name = resolver_match.url_name
        # Exclude model and action.
        parts = url_name.split("_")[:-2]
        # Return parts.
        return "_".join(parts)


@register.simple_tag(takes_context=True)
def get_app_list(context):
    request = context["request"]
    resolver_match = resolve(request.path_info)
    admin_name = resolver_match.namespace
    current_app = get_app_label(resolver_match)
    admin_site = get_admin_site(admin_name)
    app_list = admin_site.get_app_list(request)
    return get_semantic_app_list(app_list, current_app)


def get_admin_site(current_app):
    try:
        resolver_match = resolve(reverse("%s:index" % current_app))
        for func_closure in resolver_match.func.func_closure:
            if isinstance(func_closure.cell_contents, AdminSite):
                return func_closure.cell_contents
    except Exception:
        pass
    return admin.site


def get_admin_url(request, admin_site):
    try:
        url = "{}:index".format(admin_site)
        url = reverse(url)
    except Exception:
        pass
    else:
        return url


@register.simple_tag(takes_context=True)
def admin_apps(context):
    return get_app_list(context)
