document.addEventListener("DOMContentLoaded", function () {
  var questaoTextareas = document.querySelectorAll(".input-padrao-questao");
  var respostaTextareas = document.querySelectorAll(".input-padrao-respostas");

  function adjustHeight(el) {
    el.style.height = "auto"; // Redefine a altura para auto
    el.style.height = el.scrollHeight + "px"; // Define a altura para o scrollHeight
  }

  questaoTextareas.forEach(function (textarea) {
    textarea.addEventListener("input", function () {
      adjustHeight(textarea);
    });

    // Ajuste inicial
    adjustHeight(textarea);
  });

  respostaTextareas.forEach(function (textarea) {
    textarea.addEventListener("input", function () {
      adjustHeight(textarea);
    });

    // Ajuste inicial
    adjustHeight(textarea);
  });

  // Add event listeners to checkboxes to ensure only one is checked at a time
  var checkboxes = document.querySelectorAll('input[name="correta"]');
  checkboxes.forEach(function (checkbox) {
    checkbox.addEventListener("change", function () {
      if (this.checked) {
        checkboxes.forEach(function (otherCheckbox) {
          if (otherCheckbox !== checkbox) {
            otherCheckbox.checked = false;
          }
        });
      }
    });
  });
});
