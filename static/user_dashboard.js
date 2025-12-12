// SIMPLE TAB SWITCHING

const tabButtons = document.querySelectorAll(".tab-btn");

const tabPages = document.querySelectorAll(".tab-page");

tabButtons.forEach(btn => {

    btn.addEventListener("click", () => {

        document.querySelector(".tab-btn.active").classList.remove("active");

        btn.classList.add("active");

        document.querySelector(".tab-page.active").classList.remove("active");

        document.getElementById(btn.dataset.tab).classList.add("active");

    });

});

// PLACEHOLDER DATA (Flask will replace these)

document.getElementById("user-name").textContent = "Michael";

document.getElementById("profile-name").textContent = "Michael B";

document.getElementById("profile-email").textContent = "mike@example.com";

document.getElementById("profile-dob").textContent = "2008-05-16";

document.getElementById("profile-member-since").textContent = "2025";

// Example Loyalty

document.getElementById("loyalty-points").textContent = "120";

// Example Booking Form Logic

document.getElementById("booking-form").addEventListener("submit", (e) => {

    e.preventDefault();

    const visit = document.getElementById("visit-type").value;

    const date = document.getElementById("visit-date").value;

    alert("Booking submitted (placeholder). Backend coming next.");

});

// Logout

document.getElementById("logout-btn").onclick = () => {

    window.location.href = "/logout"; // Flask route

};
 