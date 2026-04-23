(function () {
  "use strict";

  function addStyles() {
    if (document.getElementById("evaluacion-esquema-inline-state-style")) {
      return;
    }

    const style = document.createElement("style");
    style.id = "evaluacion-esquema-inline-state-style";
    style.textContent = `
      .evaluacion-inline-readonly table {
        opacity: 0.68;
      }

      .evaluacion-inline-readonly input:not([type="hidden"]),
      .evaluacion-inline-readonly select,
      .evaluacion-inline-readonly textarea,
      .evaluacion-inline-readonly .add-row a {
        pointer-events: none;
      }

      .evaluacion-inline-readonly .add-row {
        display: none;
      }

      .evaluacion-inline-state-message {
        background: #fff8e5;
        border-left: 4px solid #d8a100;
        color: #5b4300;
        margin: 0 0 12px;
        padding: 10px 12px;
      }
    `;
    document.head.appendChild(style);
  }

  function getComponentesGroup() {
    return document.getElementById("componentes-group");
  }

  function setInlineReadonly(isReadonly) {
    const group = getComponentesGroup();
    if (!group) {
      return;
    }

    group.classList.toggle("evaluacion-inline-readonly", isReadonly);
    setStateMessage(group, isReadonly);

    group
      .querySelectorAll('input:not([type="hidden"]), select, textarea')
      .forEach((field) => {
        if (isReadonly) {
          field.dataset.previousTabindex = field.getAttribute("tabindex") || "";
          field.setAttribute("tabindex", "-1");
          field.setAttribute("aria-disabled", "true");
          if ("readOnly" in field) {
            field.readOnly = true;
          }
        } else {
          if (field.dataset.previousTabindex) {
            field.setAttribute("tabindex", field.dataset.previousTabindex);
          } else {
            field.removeAttribute("tabindex");
          }
          field.removeAttribute("aria-disabled");
          if ("readOnly" in field) {
            field.readOnly = false;
          }
        }
      });
  }

  function setStateMessage(group, isReadonly) {
    let message = group.querySelector(".evaluacion-inline-state-message");
    if (!message) {
      message = document.createElement("p");
      message.className = "evaluacion-inline-state-message";
      message.textContent =
        "Este esquema no está disponible para evaluación. Los componentes se conservan para consulta histórica.";
      const fieldset = group.querySelector("fieldset");
      const table = group.querySelector("table");
      if (fieldset && table) {
        fieldset.insertBefore(message, table);
      }
    }

    message.hidden = !isReadonly;
  }

  function syncInlineState() {
    const activo = document.getElementById("id_activo");
    if (!activo) {
      return;
    }

    setInlineReadonly(!activo.checked);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const activo = document.getElementById("id_activo");
    if (!activo) {
      return;
    }

    addStyles();
    syncInlineState();
    activo.addEventListener("change", syncInlineState);
  });
})();
