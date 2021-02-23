const rootDir = JSON.parse(document.getElementById('root-dir').textContent);
const clearButton = document.getElementById("clearSelections");
const compareButton = document.getElementById("compare");
const checkboxes = document.getElementsByName("checkbox");
const checkedJSON = window.sessionStorage.getItem("checked") || "[]";
let checked = JSON.parse(checkedJSON);
let checkboxesDisabled = false;
updateButtonStates();
initializeCheckboxes();
updateCheckboxStates();

function initializeCheckboxes() {
    for (const checkbox of checkboxes) {

        // check checkboxes again after a reload
        if (checked.indexOf(checkbox.getAttribute("algorithm")) !== -1) {
            checkbox.checked = true;
        }

        checkbox.onclick = function () {
            var algorithm_id = this.getAttribute('algorithm');
            if (checked.includes(algorithm_id)) {
                checked = checked.filter(id => id !== algorithm_id);
                window.sessionStorage.setItem("checked", JSON.stringify(checked));
            } else if (checked.length < 2) {
                checked.push(algorithm_id);
                window.sessionStorage.setItem("checked", JSON.stringify(checked));
            }
            updateButtonStates();
            updateCheckboxStates();
        }, { passive: true };
    }
}

function updateCheckboxStates() {
    if (checkboxesDisabled && checked.length !== 2) {
        checkboxesDisabled = false;
        enableCheckboxes();
    }
    if (!checkboxesDisabled && checked.length === 2) {
        checkboxesDisabled = true;
        disableCheckboxes();
    }
}

// disables all checkboxes except the ones that are currently selected
function disableCheckboxes() {
    checkboxesDisabled = true;
    for (const checkbox of checkboxes) {
        checkbox.disabled = true;
        if (checkbox.checked) {
            checkbox.disabled = false;
        }
    };
}

function enableCheckboxes() {
    for (const checkbox of checkboxes) {
        checkbox.disabled = false;
    };
}

// enables and disables compare and clear selections
// buttons based on how many algorithms are currently selected
function updateButtonStates() {
    if (checked.length !== 2) {
        compareButton.href = ""; // disables the link
        compareButton.classList.add('disabled');
    } else {
        compareButton.href = window.location.protocol + "//" + window.location.host
          + "/" + rootDir + "compare/" + checked[0] + "/" + checked[1];
        compareButton.classList.remove("disabled");
    }

    clearButton.disabled = checked.length === 0;
}

// clears storage and reloads the page to initialize everything again
clearButton.onclick = () => {
    window.sessionStorage.removeItem("checked");
    window.location.reload();
};