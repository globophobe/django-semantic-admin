from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import HttpRequest, JsonResponse


class SemanticAutocompleteJsonView(AutocompleteJsonView):
    """Semantic autocomplete JSON view"""

    # TODO: Delete overridden get method once serialize_result is released
    # in a future Django version
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """
        Return a JsonResponse with search results of the form:
        {
            results: [{id: "123" text: "foo"}],
            pagination: {more: true}
        }
        """
        (
            self.term,
            self.model_admin,
            self.source_field,
            to_field_name,
        ) = self.process_request(request)

        if not self.has_perm(request):
            raise PermissionDenied

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse(
            {
                # BEGIN CUSTOMIZATION #
                "results": [
                    self.serialize_result(obj, to_field_name)
                    for obj in context["object_list"]
                ],
                # END CUSTOMIZATION #
                "pagination": {"more": context["page_obj"].has_next()},
            }
        )

    def serialize_result(self, obj: models.Model, to_field_name: str) -> dict:
        """
        Convert the provided model object to a dictionary that is added to the
        results list.
        """
        return {
            "id": str(getattr(obj, to_field_name)),
            "name": getattr(obj, "semantic_autocomplete", str(obj)),
            "text": str(obj),
        }
