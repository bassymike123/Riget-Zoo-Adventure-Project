document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // this shows success message //
    document.getElementById('formSuccess').style.display = "block";

    // clears fields //
    this.reset();
});

// fade-up scroll animation //
const elements = document.querySelectorAll('.fade-up');
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
});

elements.forEach(el => observer.observe(el));
