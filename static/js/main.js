/* ============================================================
   CYBER AWARENESS MONTH 2026
   MAIN JAVASCRIPT
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    // --------------------------------------------------------
    // Automatically hide flash messages
    // --------------------------------------------------------

    const flashMessages = document.querySelectorAll(".flash");

    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";

            message.style.transform = "translateY(-5px)";

            message.style.transition = "0.4s ease";

            setTimeout(function () {
                message.remove();
            }, 400);

        }, 5000);

    });


    // --------------------------------------------------------
    // Password visibility helper
    // --------------------------------------------------------

    const passwordFields = document.querySelectorAll(
        'input[type="password"]'
    );

    passwordFields.forEach(function (field) {

        field.addEventListener("focus", function () {

            field.style.borderColor =
                "rgba(56, 217, 169, 0.6)";

        });

        field.addEventListener("blur", function () {

            field.style.borderColor = "";

        });

    });


    // --------------------------------------------------------
    // Simple button loading state
    // --------------------------------------------------------

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton =
                form.querySelector('button[type="submit"]');

            if (submitButton) {

                submitButton.style.opacity = "0.8";

                submitButton.style.pointerEvents = "none";

                submitButton.textContent = "Please wait...";

            }

        });

    });

});
