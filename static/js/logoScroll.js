document.addEventListener("DOMContentLoaded", function() {
    const track = document.querySelector(".logo-track");
    const logos = Array.from(track.children);
    const clone = logos.map(logo => logo.cloneNode(true));
    clone.forEach(c => track.appendChild(c));
});

