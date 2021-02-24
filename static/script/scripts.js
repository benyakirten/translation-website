const convertUnits = JSON.parse(localStorage.getItem("g_f_cu"));
const simpleFormatting = JSON.parse(localStorage.getItem("g_f_sf"));

document.addEventListener('DOMContentLoaded', () => {
    const input = document.querySelector(".form__input");
    const website = document.querySelector(".form__select");
    
    const checkboxConvertUnits = document.querySelector("#convert");
    const spanConvertUnits = document.querySelector('#checkbox-units__span');

    const checkboxSimpleFormatting = document.querySelector("#simple");
    const spanSimpleFormatting = document.querySelector('#checkbox-simple-output__span');

    const CONVERT_UNITS_TEXT = ["Convert units", "Don't convert units"];
    const SIMPLE_FORMATTING_TEXT = ["Recipe Formatted", "Plain Formatting"];

    initCheckbox(convertUnits, checkboxConvertUnits, spanConvertUnits, CONVERT_UNITS_TEXT)
    initCheckbox(simpleFormatting, checkboxSimpleFormatting, spanSimpleFormatting, SIMPLE_FORMATTING_TEXT)

    function initCheckbox(status, checkbox, span, text) {
        if (status) {
            checkbox.checked = status
            span.innerText = text[0]
        } else {
            checkbox.checked = false
            span.innerText = text[1]  
        }
    }
    

    checkboxConvertUnits.addEventListener('change',
        e => toggleChecked(e, spanConvertUnits, CONVERT_UNITS_TEXT, "g_f_cu"));
    checkboxSimpleFormatting.addEventListener('change',
        e => toggleChecked(e, spanSimpleFormatting, SIMPLE_FORMATTING_TEXT, "g_f_sf"));

    function toggleChecked (e, span, textArray, localString) {
        span.innerText = e.target.checked ? textArray[0] : textArray[1];
        localStorage.setItem(localString, e.target.checked)
    }

    input.addEventListener('input', e => {
        if (e.target.value.includes("ricette.giallozafferano")) {
            website.value = 'gz';
        } else if (e.target.value.includes("fattoincasa")) {
            website.value = 'fc';
        } else if (e.target.value.includes("mollichedizucchero")) {
            website.value = 'mz';
        } else if (e.target.value.includes("allacciateilgrembiule")) {
            website.value = 'ag';
        } else if (e.target.value.includes("primipiattiricette")) {
            website.value = 'rm';
        }
    });
});