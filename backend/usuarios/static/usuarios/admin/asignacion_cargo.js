(function () {
  "use strict";

  const CARGOS_CON_CARRERA = new Set([
    "JEFE_SUB_PLAN_EVAL",
    "JEFE_SUB_EJEC_CTR",
  ]);

  function toggleCarreraField() {
    const cargoField = document.getElementById("id_cargo_codigo");
    const carreraField = document.getElementById("id_carrera");
    if (!cargoField || !carreraField) {
      return;
    }

    const carreraRow = carreraField.closest(".form-row") || carreraField.closest(".form-group");
    const cargoUsaCarrera = CARGOS_CON_CARRERA.has(cargoField.value);

    if (carreraRow) {
      carreraRow.style.display = cargoUsaCarrera ? "" : "none";
    }

    carreraField.disabled = !cargoUsaCarrera;
    if (!cargoUsaCarrera) {
      carreraField.value = "";
    }
  }

  window.addEventListener("load", function () {
    const cargoField = document.getElementById("id_cargo_codigo");
    toggleCarreraField();

    if (cargoField) {
      cargoField.addEventListener("change", toggleCarreraField);
    }
  });
})();
