document.addEventListener('DOMContentLoaded', () => {
    // This page will have a back button
    // Rather than program it in page, I decided to offload it into this script
    document.querySelector(".btn")
        .addEventListener('click', () => {
            window.history.back();
        });
});