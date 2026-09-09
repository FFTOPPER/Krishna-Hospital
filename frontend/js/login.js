const API="https://krishna-hospital-backend.onrender.com";

const loginForm = document.getElementById("loginForm");
const loginId = document.getElementById("loginId");
const loginPassword = document.getElementById("loginPassword");
const loginError = document.getElementById("loginError");

loginForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    loginError.innerText = "";

    const emailOrPhone = loginId.value.trim();
    const password = loginPassword.value;

    if (!emailOrPhone || !password) {

        loginError.innerText = "Please enter both fields.";
        return;

    }

    try {

        const res = await fetch(`${API}/login`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                email_or_phone: emailOrPhone,
                password: password

            })

        });

        const data = await res.json();

        if (data.success) {

            // Save login status
            localStorage.setItem("patient_logged_in", "true");

            // Database Patient ID (used for API calls)
            localStorage.setItem("patient_numeric_id", data.patient_id);

            // Email or Phone (used for display)
            localStorage.setItem(
                "patient_id",
                data.email_or_phone || emailOrPhone
            );

            // Redirect after successful login
            window.location.href = "dashboard.html";

        } else {

            loginError.innerText =
                data.message || "Incorrect credentials.";

        }

    } catch (err) {

        console.error(err);
        loginError.innerText = "Unable to connect to the server.";

    }

});