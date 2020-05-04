from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.http import Http404, JsonResponse


class SemanticAutocompleteJsonView(AutocompleteJsonView):
    def get(self, request, require_search_fields=True, *args, **kwargs):
        """
        Return a JsonResponse with search results of the form:
        {
            results: [{id: "123" text: "foo"}],
            pagination: {more: true}
        }
        """
        # BEGIN CUSTOMIZATION #
        if require_search_fields and not self.model_admin.get_search_fields(request):
            # END CUSTOMIZATION #
            raise Http404(
                "%s must have search_fields for the autocomplete_view."
                % type(self.model_admin).__name__
            )
        if not self.has_perm(request):
            return JsonResponse({"error": "403 Forbidden"}, status=403)

        self.term = request.GET.get("term", "")
        self.paginator_class = self.model_admin.paginator
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse(
            {
                # BEGIN CUSTOMIZATION #
                "results": [
                    {
                        "id": str(obj.pk),
                        "name": getattr(obj, "semantic_autocomplete", str(obj)),
                        "text": str(obj),
                    }
                    for obj in context["object_list"]
                ],
                # END CUSTOMIZATION #
                "pagination": {"more": context["page_obj"].has_next()},
            }
        )
