// Simple DOM interactions for A Tiempo?.
// Developed with assistance from OpenAI Codex.

document.addEventListener("DOMContentLoaded", function () {
    // Update the examples when the user changes the comparison type
    const compareKind = document.querySelector("#compare-kind");
    const compareForm = document.querySelector("#compare-form");
    const compareInputs = document.querySelectorAll("[data-compare-input]");
    const compareHint = document.querySelector("#compare-hint");

    function updateCompareHelp() {
        if (!compareKind) {
            return;
        }

        let placeholder = "AR 1458";
        let hint = compareForm.dataset.flightHint;

        if (compareKind.value === "route") {
            placeholder = "AEP-COR";
            hint = compareForm.dataset.routeHint;
        } else if (compareKind.value === "airline") {
            placeholder = "AR";
            hint = compareForm.dataset.airlineHint;
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

    // Open and close the list of routes in a native dialog
    const routeDialog = document.querySelector("#route-dialog");
    const routeDialogOpen = document.querySelector("[data-route-dialog-open]");
    const routeDialogClose = document.querySelector("[data-route-dialog-close]");

    if (routeDialog && routeDialogOpen && routeDialogClose) {
        routeDialogOpen.addEventListener("click", function () {
            routeDialog.showModal();
        });

        routeDialogClose.addEventListener("click", function () {
            routeDialog.close();
        });

        routeDialog.addEventListener("click", function (event) {
            // A click on the dark area outside the box also closes the dialog
            if (event.target === routeDialog) {
                routeDialog.close();
            }
        });

    }
});
