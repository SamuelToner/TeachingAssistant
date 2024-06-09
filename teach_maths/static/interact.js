const body = document.querySelector("body");
const toggle = document.querySelector("#toggle");
const sunIcon = document.querySelector(".toggle .bxs-sun");
const moonIcon = document.querySelector(".toggle .bx-moon");
const h1s = document.querySelectorAll("h1"); // Select all h1 elements
const h2s = document.querySelectorAll("h2"); // Select all h2 elements
const inputs = document.querySelectorAll("input"); // Select all input elements
const textareas = document.querySelectorAll("textarea"); // Select all textarea elements
const container = document.querySelector(".container"); // Select the container element
const lightParagraphs = document.querySelectorAll(".view-post-page.light p");
const darkParagraphs = document.querySelectorAll(".view-post-page.dark p");
const lis = document.querySelectorAll("li");

function initTinyMCE(skin) {
    // Check if the #content element exists
    if (document.querySelector('#content')) {
        tinymce.init({
            selector: '#content',
            skin: skin
        });
    }
}

// Check for saved 'darkMode' in localStorage
if (localStorage.getItem('darkMode')) {
    body.classList.add('dark');
    container.classList.add('dark'); // Add the 'dark' class to the container
    [h1s, h2s, inputs, textareas, lis, lightParagraphs, darkParagraphs].forEach(elements => elements.forEach(el => el.classList.add('dark')));
    sunIcon.className = "bx bx-sun";
    moonIcon.className = "bx bxs-moon";
    toggle.checked = true;
    initTinyMCE('oxide-dark');
} else {
    container.classList.add('light'); // Add the 'light' class to the container
    [h1s, h2s, lis, inputs, textareas, lightParagraphs, darkParagraphs].forEach(elements => elements.forEach(el => el.classList.add('light')));
    initTinyMCE('oxide');
}

toggle.addEventListener("change", () => {
    body.classList.toggle("dark");
    container.classList.toggle("dark"); // Toggle the 'dark' class on the container
    container.classList.toggle("light"); // Toggle the 'light' class on the container
    [h1s, h2s, lis, inputs, textareas, lightParagraphs, darkParagraphs].forEach(elements => {
        elements.forEach(el => {
            el.classList.toggle("dark");
            el.classList.toggle("light");
        });
    });
    sunIcon.className = sunIcon.className == "bx bxs-sun" ? "bx bx-sun" : "bx bxs-sun";
    moonIcon.className = moonIcon.className == "bx bxs-moon" ? "bx bx-moon" : "bx bxs-moon";

    // Check if TinyMCE is present on the page
    if (window.tinymce && tinymce.editors.length > 0) {
        // Remove the existing TinyMCE editor
        tinymce.remove();

        // Reinitialize TinyMCE with the appropriate skin
        if (body.classList.contains('dark')) {
            initTinyMCE('oxide-dark');
        } else {
            initTinyMCE('oxide');
        }
    }

    if (body.classList.contains('dark')) {
        localStorage.setItem('darkMode', true);
    } else {
        localStorage.removeItem('darkMode');
    }
});