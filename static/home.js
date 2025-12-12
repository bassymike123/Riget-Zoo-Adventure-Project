document.addEventListener('DOMContentLoaded', () => {
    // adding pressed effect with pills


    const controls = document.querySelectorAll('.btn, .pill, .loyalty-pill a');


    controls.forEach(el => {
        el.addEventListener('mousedown', () => {
            el.style.transform = 'translateY(-1px) scale(0.995)';
        });

        el.addEventListener('mouseup', () => {
            el.style.transform = '';
        });

        el.addEventListener('mouseleave', () => {
            el.style.transform = '';
        });
    });

    // to prevent double submit for login //
    const primary = document.querySelector('.btn-primary');

    if (primary) {
        primary.addEventListener('click', (e) => {
            if (primary.classList.contains('disbaled')) {
                e.preventDefault();
                return;
            }

            primary.classList.add('disabled');
            setTimeout(() => primary.classList.remove('disabled'), 600);
        });
    }
}); 


// extra animation for homepage card //
const card = document.querySelector('.hero-image-card');
card.addEventListener('mousemove', (e) => {
   const rect = card.getBoundingClientRect();
   const x = e.clientX - rect.left;
   const y = e.clientY - rect.top;
   const tiltX = (y / rect.height - 0.5) * 10;
   const tiltY = (x / rect.width - 0.5) * -10;
   card.style.transform = `rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale(1.05)`;
});
card.addEventListener('mouseleave', () => {
   card.style.transform = "rotateX(0) rotateY(0) scale(1)";
   card.style.transition = "transform 0.4s ease";
});


(function(d){
   var s = d.createElement("script");
   s.setAttribute("data-account", "FREE");
   s.setAttribute("src", "https://cdn.userway.org/widget.js");
   d.body.appendChild(s);
})(document);


document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("cookie-popup");
    const overlay = document.getElementById("cookie-overlay");
    // if no choice sohw pop up and disbale the home page //
    if (!localStorage.getItem("cookieChoice")) {
        popup.style.display = "block";
        overlay.style.display = "block";
        document.body.style.overflow = "hidden"; // disables scroll on page
    }
    function closePopup(choice) {
        localStorage.setItem("cookieChoice", choice);
        popup.style.display = "none";
        overlay.style.display = "none";
        document.body.style.overflow = ""; // renables scroll on page
    }
    document.getElementById("accept-cookies").addEventListener("click", () => {
        closePopup("accepted");
    });
    document.getElementById("reject-cookies").addEventListener("click", () => {
        closePopup("rejected");
    });
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
