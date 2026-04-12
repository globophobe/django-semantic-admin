(function (window, $) {
  if (!$) {
    return;
  }

  function isInlineTemplateField($select) {
    return ($select.attr("name") || "").indexOf("__prefix__") !== -1;
  }

  function collectSelects(root, selector) {
    var $root = root ? $(root) : $(document);
    if ($root.is(selector)) {
      return $root;
    }
    return $root.find(selector);
  }

  function initDropdownSelect(select) {
    var $select = $(select);

    if (
      $select.hasClass("initialized") ||
      $select.hasClass("admin-autocomplete") ||
      isInlineTemplateField($select)
    ) {
      return;
    }

    $select.dropdown({
      clearable: true,
      fullTextSearch: true,
      forceSelection: false,
    });
    $select.addClass("initialized");
  }

  function buildAutocompleteUrl($select) {
    var url = $select.data("ajax--url");
    if (!url) {
      return null;
    }

    url += "?app_label=" + $select.data("app-label");
    url += "&model_name=" + $select.data("model-name");
    url += "&field_name=" + $select.data("field-name");
    url += "&term={query}";
    return url;
  }

  function initAutocompleteSelect(select) {
    var $select = $(select);
    var url;

    if ($select.hasClass("initialized") || isInlineTemplateField($select)) {
      return;
    }

    url = buildAutocompleteUrl($select);
    if (!url) {
      return;
    }

    $select.dropdown({
      apiSettings: {
        url: url,
        onResponse: function (response) {
          response.results = response.results.map(function (result) {
            return Object.assign(
              { value: result.id, name: result.name || result.text },
              result
            );
          });
          return response;
        },
        cache: false,
      },
      clearable: true,
      fullTextSearch: true,
      forceSelection: false,
      saveRemoteData: false,
    });
    $select.addClass("initialized");
  }

  function initDropdownSelects(root) {
    collectSelects(root, ".ui.dropdown select")
      .not(".admin-autocomplete")
      .each(function () {
        initDropdownSelect(this);
      });
  }

  function initAutocompleteSelects(root) {
    collectSelects(root, ".admin-autocomplete").each(function () {
      initAutocompleteSelect(this);
    });
  }

  window.semanticAdminInitDropdownSelects = initDropdownSelects;
  window.semanticAdminInitAutocompleteSelects = initAutocompleteSelects;

  $(document).ready(function () {
    initAutocompleteSelects(document);
  });
})(window, (window.django && window.django.jQuery) || window.jQuery || window.$);
