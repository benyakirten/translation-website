document.addEventListener('DOMContentLoaded', () => {

    input = document.querySelector(".form__input");
    website = document.querySelector(".form__select");
    checkbox = document.querySelector(".form__checkbox__input");
    span = document.querySelector('.form__checkbox__span');

    checkbox.addEventListener('change', e => {
        span.innerText = e.target.checked ? "Convert units" : "Don't convert units";
    });

    input.addEventListener('input', e => {
        if (e.target.value.includes("giallozafferano")) {
            website.value = 'gz';
        } else if (e.target.value.includes("fattoincasa")) {
            website.value = 'fc';
        }
    });
});