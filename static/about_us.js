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


(function(d){
   var s = d.createElement("script");
   s.setAttribute("data-account", "FREE");
   s.setAttribute("src", "https://cdn.userway.org/widget.js");
   d.body.appendChild(s);
})(document);