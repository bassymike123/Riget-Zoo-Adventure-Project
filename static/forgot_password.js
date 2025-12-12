function enableButton() {
    const email = document.getElementById("email").value
    const btn = document.getElementById("sendOtpBtn");
    btn.disabled = (email.trim() == "");
}