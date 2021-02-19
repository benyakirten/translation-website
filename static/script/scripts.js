document.addEventListener('DOMContentLoaded', () => {

    input = document.querySelector(".form__input");
    website = document.querySelector(".form__select");
    checkbox = document.querySelector(".form__checkbox__input");
    span = document.querySelector('.form__checkbox__span');

    checkbox.addEventListener('change', e => {
        span.innerText = e.target.checked ? "Convert units" : "Don't convert units";
    });

    input.addEventListener('input', e => {
        if (e.target.value.includes("ricette.giallozafferano")) {
            website.value = 'gz';
        } else if (e.target.value.includes("fattoincasa")) {
            website.value = 'fc';
        } else if (e.target.value.includes("mollichedizucchero")) {
            website.value = 'mz';
        } else if (e.target.value.includes("allacciateilgrembiule")) {
            website.value = 'ag';
        }
    });
    // I would like to make this more scalable, but for my two-page app, this is enough
    if (document.querySelector("title").includes("Translate a recipe")) {
        input.focus();
    }
});