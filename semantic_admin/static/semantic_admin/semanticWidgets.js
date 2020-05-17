function semanticChooser() {
  $(".admin-autocomplete")
    .not(".initialized")
    .not("[name*=__prefix__]")
    .each(function() {
      // Reverse lookup id from hidden input, if any.
      var id = $(this).attr("id");
      var optionValue = $(`#${id}-value`).val();
      if (optionValue) {
        var url = $(this).data("ajax-url");
        var u =
          url.substring(0, url.length - 1) + `-reverse/?id=${optionValue}`;
        fetch(u)
          .then(response => response.json())
          .then(data => {
            var { results } = data;
            if (results && results.length) {
              results.forEach(({ id, text }) => {
                $(this).append(new Option(text, id));
              });
            }
          });
      }
      // Initialize dropdown.
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

function semanticDropdown() {
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

function semanticCheckbox() {
  $(".ui.checkbox")
    .not(".initialized")
    .not("[name*=__prefix__]")
    .each(function() {
      $(this).checkbox();
      $(this).addClass("initialized");
    });
}
