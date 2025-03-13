"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll("form.delete, form.complete_all");
  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      e.stopPropagation();

      const msg = "Are you sure?";
      if (confirm(msg)) e.target.submit();
    });
  });
});
