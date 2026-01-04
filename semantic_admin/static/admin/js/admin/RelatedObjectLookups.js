/*global SelectBox, interpolate*/
// Handles related-objects functionality: lookup link for raw_id_fields
// and Add Another links.

(function($) {
  "use strict";

  // IE doesn't accept periods or dashes in the window name, but the element IDs
  // we use to generate popup window names may contain them, therefore we map them
  // to allowed characters in a reversible way so that we can locate the correct
  // element when the popup window is dismissed.
  function id_to_windowname(text) {
    text = text.replace(/\./g, "__dot__");
    text = text.replace(/\-/g, "__dash__");
    return text;
  }

  function windowname_to_id(text) {
    text = text.replace(/__dot__/g, ".");
    text = text.replace(/__dash__/g, "-");
    return text;
  }

  function showAdminPopup(triggeringLink, name_regexp, add_popup) {
    var name = triggeringLink.id.replace(name_regexp, "");
    name = id_to_windowname(name);
    var href = triggeringLink.href;
    if (add_popup) {
      if (href.indexOf("?") === -1) {
        href += "?_popup=1";
      } else {
        href += "&_popup=1";
      }
    }
    var win = window.open(
      href,
      name,
      "height=500,width=800,resizable=yes,scrollbars=yes"
    );
    win.focus();
    return false;
  }

  function showRelatedObjectLookupPopup(triggeringLink) {
    return showAdminPopup(triggeringLink, /^lookup_/, true);
  }

  function dismissRelatedLookupPopup(win, chosenId) {
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (
      elem.className.indexOf("vManyToManyRawIdAdminField") !== -1 &&
      elem.value
    ) {
      elem.value += "," + chosenId;
    } else {
      document.getElementById(name).value = chosenId;
    }
    win.close();
  }

  function showRelatedObjectPopup(triggeringLink) {
    return showAdminPopup(triggeringLink, /^(change|add|delete)_/, false);
  }

  function updateRelatedObjectLinks(triggeringLink) {
    var $this = $(triggeringLink);
    // BEGIN CUSTOMIZATION
    // Find links within the same .related-widget-wrapper
    var wrapper = $this.closest(".related-widget-wrapper");
    var siblings = wrapper.find(".view-related, .change-related, .delete-related");
    // END CUSTOMIZATION
    if (!siblings.length) {
      return;
    }
    var value = $this.val();
    if (value) {
      siblings.each(function() {
        var elm = $(this);
        elm.attr(
          "href",
          elm.attr("data-href-template").replace("__fk__", value)
        );
        elm.removeAttr("aria-disabled");
      });
    } else {
      siblings.removeAttr("href");
      siblings.attr("aria-disabled", "true");
    }
  }

  // BEGIN CUSTOMIZATION - Django 6.0 cross-select sync
  function updateRelatedSelectsOptions(currentSelect, win, objId, newRepr, newId, skipIds) {
    // After create/edit a model from the options next to the current
    // select (+ or pencil) update ForeignKey PK of the rest of selects
    // in the page.
    var path = win.location.pathname;
    // Extract the model from the popup url '.../<model>/add/' or
    // '.../<model>/<id>/change/' depending the action (add or change).
    var pathParts = path.split('/');
    var modelName = pathParts[pathParts.length - (objId ? 4 : 3)];
    // Select elements with a specific model reference and context of "available-source".
    var selectsRelated = document.querySelectorAll(
      '[data-model-ref="' + modelName + '"] [data-context="available-source"]'
    );

    selectsRelated.forEach(function(select) {
      if (currentSelect === select || (skipIds && skipIds.indexOf(select.id) !== -1)) {
        return;
      }

      var option = select.querySelector('option[value="' + objId + '"]');

      if (!option) {
        option = new Option(newRepr, newId);
        select.options.add(option);
        // Update SelectBox cache for related fields.
        if (window.SelectBox !== undefined && !SelectBox.cache[currentSelect.id]) {
          SelectBox.add_to_cache(select.id, option);
          SelectBox.redisplay(select.id);
        }
        return;
      }

      option.textContent = newRepr;
      option.value = newId;
    });
  }
  // END CUSTOMIZATION

  function dismissAddRelatedObjectPopup(win, newId, newRepr) {
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem) {
      var elemName = elem.nodeName.toUpperCase();
      if (elemName === "SELECT") {
        elem.options[elem.options.length] = new Option(
          newRepr,
          newId,
          true,
          true
        );
        updateRelatedSelectsOptions(elem, win, null, newRepr, newId);
      } else if (elemName === "INPUT") {
        if (
          elem.className.indexOf("vManyToManyRawIdAdminField") !== -1 &&
          elem.value
        ) {
          elem.value += "," + newId;
        } else {
          elem.value = newId;
        }
      }
      // Trigger a change event to update related links if required.
      $(elem).trigger("change");
    } else {
      var toId = name + "_to";
      var toElem = document.getElementById(toId);
      var o = new Option(newRepr, newId);
      SelectBox.add_to_cache(toId, o);
      SelectBox.redisplay(toId);
      if (toElem && toElem.nodeName.toUpperCase() === "SELECT") {
        var skipIds = [name + "_from"];
        updateRelatedSelectsOptions(toElem, win, null, newRepr, newId, skipIds);
      }
    }
    win.close();
  }

  function dismissChangeRelatedObjectPopup(win, objId, newRepr, newId) {
    var id = windowname_to_id(win.name).replace(/^edit_/, "");
    var selectsSelector = interpolate("#%s, #%s_from, #%s_to", [id, id, id]);
    var selects = $(selectsSelector);
    selects.find("option").each(function() {
      if (this.value === objId) {
        this.textContent = newRepr;
        this.value = newId;
      }
    });
    updateRelatedSelectsOptions(selects[0], win, objId, newRepr, newId);
    win.close();
  }

  function dismissDeleteRelatedObjectPopup(win, objId) {
    var id = windowname_to_id(win.name).replace(/^delete_/, "");
    var selectsSelector = interpolate("#%s, #%s_from, #%s_to", [id, id, id]);
    var selects = $(selectsSelector);
    selects
      .find("option")
      .each(function() {
        if (this.value === objId) {
          $(this).remove();
        }
      })
      .trigger("change");
    win.close();
  }

  // Global for testing purposes
  window.id_to_windowname = id_to_windowname;
  window.windowname_to_id = windowname_to_id;

  window.showRelatedObjectLookupPopup = showRelatedObjectLookupPopup;
  window.dismissRelatedLookupPopup = dismissRelatedLookupPopup;
  window.showRelatedObjectPopup = showRelatedObjectPopup;
  window.updateRelatedObjectLinks = updateRelatedObjectLinks;
  window.dismissAddRelatedObjectPopup = dismissAddRelatedObjectPopup;
  window.dismissChangeRelatedObjectPopup = dismissChangeRelatedObjectPopup;
  window.dismissDeleteRelatedObjectPopup = dismissDeleteRelatedObjectPopup;

  // Kept for backward compatibility
  window.showAddAnotherPopup = showRelatedObjectPopup;
  window.dismissAddAnotherPopup = dismissAddRelatedObjectPopup;

  $(document).ready(function() {
    $("a[data-popup-opener]").click(function(event) {
      event.preventDefault();
      opener.dismissRelatedLookupPopup(window, $(this).data("popup-opener"));
    });
    // Only bind to links with data-popup="yes" (add/change/delete).
    // View links navigate normally without popup.
    $("body").on("click", ".related-widget-wrapper-link[data-popup='yes']", function(e) {
      e.preventDefault();
      if (this.href) {
        var event = $.Event("django:show-related", { href: this.href });
        $(this).trigger(event);
        if (!event.isDefaultPrevented()) {
          showRelatedObjectPopup(this);
        }
      }
    });
    // Trigger on 'related-widget', instead of 'related-widget-wrapper'.
    $("body").on("change", ".related-widget select", function(e) {
      var event = $.Event("django:update-related");
      $(this).trigger(event);
      if (!event.isDefaultPrevented()) {
        updateRelatedObjectLinks(this);
      }
    });
    // Trigger on 'related-widget', instead of 'related-widget-wrapper'.
    $(".related-widget select").trigger("change");
    $("body").on("click", ".related-lookup", function(e) {
      e.preventDefault();
      var event = $.Event("django:lookup-related");
      $(this).trigger(event);
      if (!event.isDefaultPrevented()) {
        showRelatedObjectLookupPopup(this);
      }
    });
  });
})(django.jQuery);
