from semantic_forms import SemanticCheckboxInput


class SemanticChangelistCheckboxInput(SemanticCheckboxInput):
    """Semantic changelist checkbox input."""

    template_name = "semantic_admin/changelist_checkbox.html"


class SemanticActionCheckboxInput(SemanticCheckboxInput):
    """Semantic action checkbox input."""

    template_name = "semantic_admin/action_checkbox.html"
