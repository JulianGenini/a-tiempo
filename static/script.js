// Simple DOM interactions for A Tiempo?.
// Developed with assistance from OpenAI Codex.

document.addEventListener("DOMContentLoaded", function () {
    const compareKind = document.querySelector("#compare-kind");
    const compareInputs = document.querySelectorAll("[data-compare-input]");
    const compareHint = document.querySelector("#compare-hint");

    function updateCompareHelp() {
        if (!compareKind) {
            return;
        }

        let placeholder = "AR 1458";
        let hint = "Example: AR 1458";

        if (compareKind.value === "route") {
            placeholder = "AEP-COR";
            hint = "Use ORIGIN-DESTINATION, for example AEP-COR.";
        } else if (compareKind.value === "airline") {
            placeholder = "AR";
            hint = "Use an airline IATA code, for example AR.";
        }

        compareInputs.forEach(function (input) {
            input.placeholder = placeholder;
        });

        if (compareHint) {
            compareHint.textContent = hint;
        }
    }

    if (compareKind) {
        compareKind.addEventListener("change", updateCompareHelp);
        updateCompareHelp();
    }
});
