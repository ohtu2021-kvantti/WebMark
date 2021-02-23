var ind;
var rootDir = JSON.parse(document.getElementById('root-dir').textContent);
console.log(rootDir)
var elements = document.getElementsByName("checkbox");
var firstStr = window.sessionStorage.getItem("first") || "0";
var secondStr = window.sessionStorage.getItem("second") || "0";
var first = JSON.parse(firstStr);
var second = JSON.parse(secondStr);
var checkboxesDisabled = false;
var checked = [];
if (first !== 0) {
    checked.push(first);
}
if (second !== 0) {
    checked.push(second);
}
updateButtonStates();

for (ind = 0; ind < elements.length; ind++) {

    // check checkboxes again after a reload
    if (checked.indexOf(elements[ind].getAttribute("algorithm")) !== -1) {
        elements[ind].checked = true;
    }

    elements[ind].onclick = function () {
        var algorithm_id = this.getAttribute('algorithm');
        if (first === algorithm_id) {
            first = 0;
            window.sessionStorage.removeItem("first");
            checked.splice(checked.indexOf(algorithm_id), 1);
        } else if (second === algorithm_id) {
            second = 0;
            window.sessionStorage.removeItem("second");
            checked.splice(checked.indexOf(algorithm_id), 1);
        } else if (second === 0) {
            second = algorithm_id;
            window.sessionStorage.setItem("second", JSON.stringify(second));
            checked.push(second);
        } else if (first === 0) {
            first = algorithm_id;
            window.sessionStorage.setItem("first", JSON.stringify(first));
            checked.push(first);
        }
        updateButtonStates();
        updateCheckboxStates();
    }, { passive: true };
}
updateCheckboxStates();

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
    var i;
    for (i = 0; i < elements.length; i++) {
        elements[i].disabled = true;
        if (elements[i].checked) {
            elements[i].disabled = false;
        }
    };
}

function enableCheckboxes() {
    var i;
    for (i = 0; i < elements.length; i++) {
        elements[i].disabled = false;
    };
}

// enables and disables compare and clear selections
// buttons based on how many algorithms are currently selected
function updateButtonStates() {
    var compareBtn = document.getElementById("compare");

    if (checked.length !== 2) {
        compareBtn.href = ""; // disables the link
        compareBtn.classList.add('disabled');
    } else {
        compareBtn.href = window.location.protocol + "//" + window.location.host
          + "/" + rootDir + "compare/" + first + "/" + second;
        compareBtn.classList.remove("disabled");
    }

    var clearBtn = document.getElementById("clearSelections");
    clearBtn.disabled = checked.length === 0;
}

// clears storage and reloads the page to initialize everything again
function clearStorageAndReload() {
    window.sessionStorage.removeItem("first");
    window.sessionStorage.removeItem("second");
    window.location.reload();
}