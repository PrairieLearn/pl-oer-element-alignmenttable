/**
 * Highlight the cell and change the value of the hidden input
 * @param {HTMLElement} button - The button that was clicked
 * @returns {void}
 */
function highlightCell(button) {
  const cellIdentifier = button.getAttribute("data-cell");
  const container = document
    .querySelector(`.input-container[data-cell="${cellIdentifier}"]`)
  if (!container) {
    return;
  }

  const hiddenInput = container.querySelector('input[type="hidden"]');
  const isHighlighted =
    hiddenInput && String(hiddenInput.value).toLowerCase() === "true";
  setAlignmentCellHighlighted(container, !isHighlighted);
}

function setAlignmentCellHighlighted(container, isHighlighted) {
  const input = container.querySelector(".alignment-number-input");
  const button = container.querySelector(".btn-highlight");
  const hiddenInput = container.querySelector('input[type="hidden"]');
  const oldClasses = [
    "striped-highlight",
    "striped-background",
    "highlight-true",
    "highlight-false",
  ];
  const newClass = isHighlighted ? "highlight-true" : "highlight-false";

  if (input) {
    input.classList.remove(...oldClasses);
    input.classList.add(newClass);
    input.style.backgroundColor = "";
  }
  if (button) {
    button.classList.remove("highlight-true", "highlight-false");
    button.classList.add(newClass);
    button.style.backgroundColor = "";
  }
  if (hiddenInput) {
    hiddenInput.value = isHighlighted ? "true" : "false";
  }
}

function isCompleteNumericValue(value) {
  const trimmed = String(value == null ? "" : value).trim();
  if (trimmed === "") {
    return true;
  }
  return Number.isFinite(Number(trimmed));
}

function isNumericInputPrefix(value) {
  const trimmed = String(value == null ? "" : value).trim();
  return /^-?(?:\d+(?:\.\d*)?|\.\d*)?$/.test(trimmed);
}

function isNumericInputKeyAllowed(event, input) {
  if (event.ctrlKey || event.metaKey || event.altKey) {
    return true;
  }
  if (isSpaceKey(event.key)) {
    return true;
  }
  if (!event.key || event.key.length !== 1) {
    return true;
  }

  const start =
    input.selectionStart === null ? input.value.length : input.selectionStart;
  const end = input.selectionEnd === null ? input.value.length : input.selectionEnd;
  const candidate =
    input.value.slice(0, start) + event.key + input.value.slice(end);
  return isNumericInputPrefix(candidate);
}

function isSpaceKey(key) {
  return key === " " || key === "Spacebar";
}

function validateNumericInput(input, requireComplete = false) {
  const valid = requireComplete
    ? isCompleteNumericValue(input.value)
    : isNumericInputPrefix(input.value);
  input.classList.toggle("alignment-input-invalid", !valid);
  input.setAttribute("aria-invalid", valid ? "false" : "true");
  return valid;
}

function rejectNumericInput(input) {
  input.classList.add("alignment-input-rejected");
  clearTimeout(input._alignmentRejectTimer);
  input._alignmentRejectTimer = setTimeout(() => {
    input.classList.remove("alignment-input-rejected");
    validateNumericInput(input);
  }, 700);
}

function updateAlignmentToolbarLayout(tableContainer) {
  const toolbar = tableContainer.querySelector(".alignment-table-toolbar");
  const tableSurface = tableContainer.querySelector(".alignment-table-surface");
  if (!toolbar || !tableSurface) {
    tableContainer.classList.remove("toolbar-below");
    return;
  }

  tableContainer.classList.remove("toolbar-below");
  const parentWidth = tableContainer.parentElement
    ? tableContainer.parentElement.clientWidth
    : window.innerWidth;
  const availableWidth = Math.min(
    parentWidth || window.innerWidth,
    document.documentElement.clientWidth || window.innerWidth
  );
  const tableWidth = tableSurface.getBoundingClientRect().width;
  const toolbarWidth = toolbar.getBoundingClientRect().width;
  const gap =
    parseFloat(window.getComputedStyle(tableContainer).columnGap) || 0;
  const wrapBuffer = 8;

  tableContainer.classList.toggle(
    "toolbar-below",
    availableWidth <= tableWidth + toolbarWidth + gap + wrapBuffer
  );
}

function hideAlignmentPopover(button) {
  if (window.bootstrap && window.bootstrap.Popover) {
    const popover = window.bootstrap.Popover.getInstance(button);
    if (popover) {
      popover.hide();
    }
  }
  button.setAttribute("aria-expanded", "false");
}

function hideOtherAlignmentPopovers(activeButton, tableContainer) {
  tableContainer
    .querySelectorAll("[data-alignment-info], [data-alignment-clear]")
    .forEach((button) => {
      if (button !== activeButton) {
        hideAlignmentPopover(button);
      }
    });
}

function toggleAlignmentPopover(button, options, tableContainer) {
  if (!window.bootstrap || !window.bootstrap.Popover) {
    return null;
  }

  hideOtherAlignmentPopovers(button, tableContainer);
  const popover = window.bootstrap.Popover.getOrCreateInstance(button, options);
  const isShown = button.getAttribute("aria-expanded") === "true";

  if (isShown) {
    popover.hide();
    button.setAttribute("aria-expanded", "false");
  } else {
    popover.show();
    button.setAttribute("aria-expanded", "true");
  }

  if (button.dataset.alignmentPopoverBound !== "true") {
    button.addEventListener("hidden.bs.popover", () => {
      button.setAttribute("aria-expanded", "false");
    });
    button.dataset.alignmentPopoverBound = "true";
  }

  return popover;
}

function clearAlignmentTable(tableContainer) {
  const numberInputs = tableContainer.querySelectorAll(".alignment-number-input");
  const boolInputs = tableContainer.querySelectorAll(".bool-input");

  numberInputs.forEach((input) => {
    input.value = 0;
    input.classList.remove("alignment-input-invalid", "alignment-input-rejected");
    input.style.backgroundColor = "";
  });

  boolInputs.forEach((input) => {
    const container = input.closest(".input-container");
    if (container) {
      setAlignmentCellHighlighted(container, false);
    } else {
      input.value = "false";
    }
  });
}

function bindAlignmentInfoButton(tableContainer) {
  const infoButton = tableContainer.querySelector("[data-alignment-info]");
  if (!infoButton) {
    return;
  }

  infoButton.addEventListener("click", (event) => {
    event.preventDefault();
    toggleAlignmentPopover(
      infoButton,
      {
        content: infoButton.getAttribute("data-alignment-popover-content") || "",
        html: true,
        placement: "auto",
        sanitize: false,
        trigger: "manual",
      },
      tableContainer
    );
  });
}

function getAlignmentPopoverTip(popover, button) {
  const describedBy = button.getAttribute("aria-describedby");
  if (describedBy) {
    const tip = document.getElementById(describedBy);
    if (tip) {
      return tip;
    }
  }
  if (popover.tip) {
    return popover.tip;
  }
  if (popover._tip) {
    return popover._tip;
  }
  if (typeof popover.getTipElement === "function") {
    return popover.getTipElement();
  }
  if (typeof popover._getTipElement === "function") {
    return popover._getTipElement();
  }
  return null;
}

function bindClearConfirmationActions(popover, clearButton, tableContainer) {
  const tip = getAlignmentPopoverTip(popover, clearButton);
  if (!tip) {
    return;
  }
  const confirmButton = tip.querySelector("[data-alignment-confirm-clear]");
  const cancelButton = tip.querySelector("[data-alignment-cancel-clear]");

  if (confirmButton) {
    confirmButton.onclick = () => {
      clearAlignmentTable(tableContainer);
      hideAlignmentPopover(clearButton);
    };
  }

  if (cancelButton) {
    cancelButton.onclick = () => {
      hideAlignmentPopover(clearButton);
    };
  }
}

function bindAlignmentClearButton(tableContainer) {
  const clearButton = tableContainer.querySelector("[data-alignment-clear]");
  if (!clearButton) {
    return;
  }

  clearButton.addEventListener("click", (event) => {
    event.preventDefault();
    const popover = toggleAlignmentPopover(
      clearButton,
      {
        content:
          '<div class="alignment-confirm-popover">' +
          '<p class="mb-2">Clear all table entries and highlighted path cells?</p>' +
          '<div class="alignment-confirm-actions">' +
          '<button type="button" class="btn btn-sm btn-danger" data-alignment-confirm-clear="true">Clear</button>' +
          '<button type="button" class="btn btn-sm btn-outline-secondary" data-alignment-cancel-clear="true">Cancel</button>' +
          "</div>" +
          "</div>",
        html: true,
        placement: "auto",
        sanitize: false,
        trigger: "manual",
      },
      tableContainer
    );

    if (!popover) {
      if (window.confirm("Clear all table entries and highlighted path cells?")) {
        clearAlignmentTable(tableContainer);
      }
      return;
    }
    if (clearButton.getAttribute("aria-expanded") !== "true") {
      return;
    }

    bindClearConfirmationActions(popover, clearButton, tableContainer);
    clearButton.addEventListener(
      "inserted.bs.popover",
      () => bindClearConfirmationActions(popover, clearButton, tableContainer),
      { once: true }
    );
    setTimeout(
      () => bindClearConfirmationActions(popover, clearButton, tableContainer),
      0
    );
  });
}

/**
 * Use arrow keys to navigate between cells in the table and clear the table on button click
 * @returns {void}
 * @listens keydown
 * @listens click
 * @listens focus
 * @listens select
 * @listens DOMContentLoaded
 */
document.addEventListener("DOMContentLoaded", () => {
  // For each table container, handle navigation and clearing
  document
    .querySelectorAll(".alignment-table-container")
    .forEach((tableContainer) => {
      updateAlignmentToolbarLayout(tableContainer);
      bindAlignmentInfoButton(tableContainer);
      bindAlignmentClearButton(tableContainer);

      // Get all number inputs in this table
      const inputs = Array.from(
        tableContainer.querySelectorAll(".alignment-number-input")
      );

    // Sort inputs by row and column for logical navigation
    const sortedInputs = inputs.sort((a, b) => {
      const rowA = parseInt(a.closest("td").dataset.row, 10);
      const rowB = parseInt(b.closest("td").dataset.row, 10);
      const colA = parseInt(a.closest("td").dataset.col, 10);
      const colB = parseInt(b.closest("td").dataset.col, 10);
      return rowA - rowB || colA - colB;
    });

    // Add keydown event listeners to inputs in this table
    sortedInputs.forEach((input, index) => {
      if (!input.readOnly) {
        input.addEventListener("keydown", (event) => {
          if (!isNumericInputKeyAllowed(event, input)) {
            event.preventDefault();
            rejectNumericInput(input);
          }
        });
        input.addEventListener("paste", (event) => {
          const clipboard = event.clipboardData || window.clipboardData;
          const pastedText = clipboard ? clipboard.getData("text") : "";
          const start =
            input.selectionStart === null
              ? input.value.length
              : input.selectionStart;
          const end =
            input.selectionEnd === null ? input.value.length : input.selectionEnd;
          const candidate =
            input.value.slice(0, start) + pastedText + input.value.slice(end);

          if (!isNumericInputPrefix(candidate)) {
            event.preventDefault();
            rejectNumericInput(input);
          }
        });
        input.addEventListener("input", () => validateNumericInput(input));
        input.addEventListener("blur", () => validateNumericInput(input, true));
        validateNumericInput(input);
      }

      input.addEventListener("keydown", (event) => {
        let nextIndex = index;
        const currentCell = input.closest("td");
        const currentRow = parseInt(currentCell.dataset.row, 10);
        const currentCol = parseInt(currentCell.dataset.col, 10);

        switch (event.key) {
          case " ":
          case "Spacebar": {
            event.preventDefault();
            const button = currentCell.querySelector(".btn-highlight");
            if (button) {
              highlightCell(button);
            }
            return;
          }
          case "ArrowUp": // Navigate up
            event.preventDefault();
            nextIndex = sortedInputs.findIndex(
              (inp) =>
                parseInt(inp.closest("td").dataset.row, 10) ===
                  currentRow - 1 &&
                parseInt(inp.closest("td").dataset.col, 10) === currentCol
            );
            break;
          case "ArrowDown": // Navigate down
            event.preventDefault();
            nextIndex = sortedInputs.findIndex(
              (inp) =>
                parseInt(inp.closest("td").dataset.row, 10) ===
                  currentRow + 1 &&
                parseInt(inp.closest("td").dataset.col, 10) === currentCol
            );
            break;
          case "ArrowLeft": // Navigate left
            event.preventDefault();
            nextIndex = index - 1;
            break;
          case "ArrowRight": // Navigate right
            event.preventDefault();
            nextIndex = index + 1;
            break;
          default:
            return; // Do nothing for other keys
        }

        // Ensure nextIndex is valid and focus that input
        if (nextIndex >= 0 && nextIndex < sortedInputs.length) {
          const nextInput = sortedInputs[nextIndex];
          nextInput.focus();
          nextInput.select();
        }
      });
    });

  });

  window.addEventListener("resize", () => {
    document
      .querySelectorAll(".alignment-table-container")
      .forEach(updateAlignmentToolbarLayout);
  });

  if (window.ResizeObserver) {
    document
      .querySelectorAll(".alignment-table-container")
      .forEach((tableContainer) => {
        const resizeObserver = new ResizeObserver(() => {
          updateAlignmentToolbarLayout(tableContainer);
        });
        if (tableContainer.parentElement) {
          resizeObserver.observe(tableContainer.parentElement);
        } else {
          resizeObserver.observe(tableContainer);
        }
      });
  }
});
