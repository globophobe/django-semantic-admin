$(document).ready(function () {
  $('input.guess_format[type="file"]').change(function () {
    const files = this.files;
    const dropdowns = $(this.form).find("select.guess_format");

    if (files.length > 0) {
      const extension = files[0].name.split(".").pop().trim().toLowerCase();

      for (let i = 0; i < dropdowns.length; i++) {
        const dropdown = dropdowns[i];
        dropdown.selectedIndex = 0;

        let match;
        const drop = $(dropdown).parent();

        for (let j = 0; j < dropdown.options.length; j++) {
          if (extension === dropdown.options[j].text.trim().toLowerCase()) {
            const value = j - 1;
            drop.dropdown("set selected", value.toString(), false); // -1 because of the empty option
            match = true;
            break;
          }
        }
        if (!match) {
          drop.dropdown("clear");
        }
      }
    }
  });
});
