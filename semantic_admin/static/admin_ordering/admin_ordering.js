/* global django */
django.jQuery(function($) {
    function updatePlaceholderHeight(ui) {
      // set placeholder height equal to item height
      ui.placeholder.height(ui.item.outerHeight());
    }
  
    function hideHorizontalOverflow() {
      // hide body horizontal overflow while dragging row
      $("body").css("overflow-x", "hidden");
    }
  
    function autoHorizontalOverflow() {
      // reset body horizontal overflow
      $("body").css("overflow-x", "auto");
    }
  
    function enforceSortableRowsCellsSize(node) {
      // enforce row cells size while sorting rows
      node.find(">tr").each(function() {
        $(this)
          .mousedown(function() {
            $(this)
              .find("td, th")
              .each(function() {
                $(this).css("width", $(this).width());
              });
          })
          .mouseup(function() {
            $(this)
              .find("td, th")
              .each(function() {
                $(this).css("width", "auto");
              });
          });
      });
    }
  
    $(".admin-ordering-context:not(.activated)")
      .addClass("activated")
      .each(function() {
        var $sortable,
          $sortableHandle,
          $sortableInputWrapper =
            '<span class="admin-ordering-field-input-wrapper"></span>';
  
        var data = JSON.parse(this.getAttribute("data-context"));
        var inputFieldSelector = 'input[name$="-' + data.field + '"]';
  
        function updateOrdering(nodes) {
          var incOrdering = 10;
          var maxOrdering = nodes.length * incOrdering;
          nodes.each(function(index) {
            var row = $(this);
            var rowOrdering = data.fieldDesc
              ? maxOrdering - incOrdering * index
              : incOrdering * (index + 1);
            row.find(inputFieldSelector).val(rowOrdering);
            row.removeClass("row1 row2").addClass(index % 2 ? "row2" : "row1");
          });
        }
  
        if (data.field.indexOf("-") == 0) {
          data.field = data.field.substring(1);
          data.fieldDesc = true;
        } else {
          data.fieldDesc = false;
        }
  
        if (data.tabular) {
          $sortable = $("#" + data.prefix + "-group tbody");
          $sortableHandle = $sortable.find(".field-" + data.field);
          $sortableHandle.addClass("admin-ordering-field");
          if (data.fieldHideInput) {
            $sortableHandle.addClass("admin-ordering-field-hide-input");
          }
          $sortableHandle
            .find(inputFieldSelector + ':not([type="hidden"])')
            .wrap($sortableInputWrapper);
          $sortable.sortable({
            items: ">.has_original",
            handle: $sortableHandle,
            start: function(_event, ui) {
              hideHorizontalOverflow();
              updatePlaceholderHeight(ui);
              // fix ui item height
              ui.item.css("height", ui.item.outerHeight());
            },
            update: function(_event, _ui) {
              updateOrdering($(".dynamic-" + data.prefix));
            },
            stop: function(_event, ui) {
              autoHorizontalOverflow();
              // reset ui item height
              ui.item.css("height", "auto");
            }
          });
  
          enforceSortableRowsCellsSize($sortable);
        } else if (data.stacked) {
          $sortable = $("#" + data.prefix + "-group");
          $sortableHandle = $sortable.find(".field-" + data.field);
          $sortableHandle.addClass("admin-ordering-field");
          if (data.fieldHideInput) {
            $sortableHandle.addClass("admin-ordering-field-hide-input");
          }
          $sortableHandle
            .find(inputFieldSelector + ':not([type="hidden"])')
            .wrap($sortableInputWrapper);
          $sortable.sortable({
            items: ">.has_original,>>.has_original,>.last-related,>>.last-related",
            handle: ".field-" + data.field,
            start: function(_event, ui) {
              hideHorizontalOverflow();
              updatePlaceholderHeight(ui);
            },
            update: function(_event, _ui) {
              updateOrdering($(".dynamic-" + data.prefix));
            },
            stop: function(_event, _ui) {
              autoHorizontalOverflow();
            }
          });
        } else {
          $sortable = $("#result_list tbody");
          $sortableHandle = $sortable.find(".field-" + data.field);
          $sortableHandle.addClass("admin-ordering-field");
          if (data.fieldHideInput) {
            $sortableHandle.addClass("admin-ordering-field-hide-input");
          }
          if (!$sortableHandle.find("input").length) {
            return;
          }
          $sortableHandle
            .find(inputFieldSelector + ':not([type="hidden"])')
            .wrap($sortableInputWrapper);
          $sortable.sortable({
            handle: $sortableHandle,
            start: function(_event, ui) {
              hideHorizontalOverflow();
              updatePlaceholderHeight(ui);
            },
            update: function(_event, _ui) {
              updateOrdering($sortable.find("tr"));
            },
            stop: function(_event, _ui) {
              autoHorizontalOverflow();
            }
          });
  
          enforceSortableRowsCellsSize($sortable);
        }
  
        if (data.tabular || data.stacked) {
          // Yay, Django 1.9 or better!
          $(document).on("formset:added", function newForm(event, row) {
            if (row.hasClass("dynamic-" + data.prefix)) {
              updateOrdering($(".dynamic-" + data.prefix));
              $sortable.sortable('refresh');
            }
          });
        }
      });
  });