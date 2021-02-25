// CONSTANTS

// LOCAL STORAGE
const CONVERT_UNITS_LOCAL_STORAGE = "g_f_cu";
const SIMPLE_FORMATTING_LOCAL_STORAGE = "g_f_sf";

// TEXT STRINGS FOR CHECKBOXES
// NOTE: Objects are used instead of arrays to reduce the use of ternary expressions
const CONVERT_UNITS_TEXT = {
    true: "Convert units",
    false: "Don't convert units",
};
const SIMPLE_FORMATTING_TEXT = {
    true: "Recipe Formatted",
    false: "Plain Formatting",
};

// HOW TO CHANGE THE VALUES ON THE OPTIONS
const WEBSITE_TO_VALUE = {
    "ricette.giallozafferano": "gz",
    fattoincasa: "fc",
    mollichedizucchero: "mz",
    allacciateilgrembiule: "ag",
    primipiattiricette: "rm",
};

// Collecting the local storage data
const convertUnits = JSON.parse(
    localStorage.getItem(CONVERT_UNITS_LOCAL_STORAGE)
);
const simpleFormatting = JSON.parse(
    localStorage.getItem(SIMPLE_FORMATTING_LOCAL_STORAGE)
);

document.addEventListener("DOMContentLoaded", () => {
    /*
        Upon content loading, this function does the following:
        1. Initializes the text and checkboxes to equal what's set in local storage
        2. Change the label of the checkboxes and their value in local storage if they're changed
        3. Checks the input box whenever there is input for a website that it should know and
            changes the option element's value to correspond.
            It can be changed manually by the user if so desired and/or it is incorrect
            One especially good use case for this is copy and pasting a website into the element.

    */

    // The input and option
    const input = document.querySelector(".form__input");
    const optionWebsite = document.querySelector(".form__select");

    const checkboxConvertUnits = document.querySelector("#convert");
    const spanConvertUnits = document.querySelector("#checkbox-units__span");

    const checkboxSimpleFormatting = document.querySelector("#simple");
    const spanSimpleFormatting = document.querySelector(
        "#checkbox-simple-output__span"
    );

    // Our init methods will only trigger if the query selector was able to find all of the form elements
    if (
        input &&
        optionWebsite &&
        checkboxConvertUnits &&
        spanConvertUnits &&
        checkboxSimpleFormatting &&
        spanSimpleFormatting
    ) {
        // Setting initial values for the checkboxes based on local storage
        initCheckbox(
            convertUnits,
            checkboxConvertUnits,
            spanConvertUnits,
            CONVERT_UNITS_TEXT
        );
        initCheckbox(
            simpleFormatting,
            checkboxSimpleFormatting,
            spanSimpleFormatting,
            SIMPLE_FORMATTING_TEXT
        );

        // Click listeners
        checkboxConvertUnits.addEventListener("change", (e) =>
            toggleChecked(
                e,
                spanConvertUnits,
                CONVERT_UNITS_TEXT,
                CONVERT_UNITS_LOCAL_STORAGE
            )
        );
        checkboxSimpleFormatting.addEventListener("change", (e) =>
            toggleChecked(
                e,
                spanSimpleFormatting,
                SIMPLE_FORMATTING_TEXT,
                SIMPLE_FORMATTING_LOCAL_STORAGE
            )
        );

        // Checks for an applicable website to use with the corresponding option value
        input.addEventListener("input", (e) => {
            for (let key in WEBSITE_TO_VALUE) {
                if (e.target.value.includes(key)) {
                    optionWebsite.value = WEBSITE_TO_VALUE[key];
                }
            }
        });
    }

    function initCheckbox(status, checkbox, span, textArray) {
        // Using the local storage value,
        // set the checked and the text to the appropriate values
        checkbox.checked = status;
        span.innerText = textArray[status];
    }

    function toggleChecked(e, span, textArray, localString) {
        // Using the current status of the checkboxes (checked/unchecked)
        // Set the inenr text and the local storage item
        span.innerText = textArray[e.target.checked];
        localStorage.setItem(localString, e.target.checked);
    }
});
