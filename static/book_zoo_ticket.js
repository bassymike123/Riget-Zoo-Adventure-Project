const dateInput = document.getElementById("visit_date");
const timeInput = document.getElementById("visit_time");
const errorBox = document.getElementById("time-error");
const continueBtn = document.getElementById("continue-btn");

// Prevent past dates
const today = new Date().toISOString().split("T")[0];
dateInput.setAttribute("min", today);

// Opening hours config
function getOpeningHours(date) {
    const day = date.getDay(); //  0 = sunday
    // TODO: bank holiday logic later
    if (day >= 1 && day <= 5) { // Mon-Fri
        return { open: "09:00", close: "18:00" };
    }
    if (day === 6) { // Saturday
        return { open: "9:00", close: "19:00" };
    }
    if (day === 0) { // Sunday
        return { open: "10:00", close: "17:00" };
    }
}

function validateTime() {
    errorBox.style.display = "none";

    if (!dateInput.value || !timeInput.value) return true;

    const selectedDate = new Date(dateInput.value);
    const { open, close } = getOpeningHours(selectedDate);

    if (timeInput.value < open || timeInput.value > close) {
        errorBox.innerText = 
            `Selected time is outside of opening hours (${open} - ${close}).`;
        errorBox.style.display = "block";
        return false;
    }
    return true;
}

dateInput.addEventListener("change", validateTime);
timeInput.addEventListener("change", validateTime);

continueBtn.addEventListener("click", function (e) {
    if (!validateTime()) {
        e.preventDefault();
    }
});