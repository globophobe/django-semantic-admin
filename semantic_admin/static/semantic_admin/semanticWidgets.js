function semanticAutocomplete(prefix) {
  $(".admin-autocomplete")
    .not(".initialized")
    .not("[name*=__prefix__]")
    .each(function() {
      var url = $(this).data("ajax-url") + "?term={query}";
      $(this).dropdown({
        apiSettings: {
          url: url,
          onResponse: function(response) {
            response.results = response.results.map(result => {
              return Object.assign(
                { value: result.id, name: result.name || result.text },
                result
              );
            });
            return response;
          },
          cache: false
        },
        clearable: true,
        fullTextSearch: true,
        forceSelection: false,
        saveRemoteData: false
      });
      // b/c not idempotent.
      $(this).addClass("initialized");
    });
}

function semanticDropdown(prefix) {
  $(".ui.dropdown select")
    .not(".initialized")
    .not(".admin-autocomplete")
    .not("[name*=__prefix__]")
    .each(function() {
      $(this).dropdown({
        clearable: true,
        fullTextSearch: true,
        forceSelection: false // https://github.com/Semantic-Org/Semantic-UI/issues/4506
      });
      $(this).addClass("initialized");
    });
}
