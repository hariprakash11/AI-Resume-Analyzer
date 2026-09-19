document.addEventListener("DOMContentLoaded", () => {

    const passwordInput =
        document.getElementById("password");

    const passwordToggle =
        document.getElementById("passwordToggle");

    if (!passwordInput || !passwordToggle) {
        return;
    }

    passwordToggle.addEventListener("click", () => {

        const isPassword =
            passwordInput.type === "password";

        passwordInput.type =
            isPassword ? "text" : "password";

        passwordToggle.setAttribute(
            "aria-label",
            isPassword
                ? "Hide password"
                : "Show password"
        );

        passwordToggle.setAttribute(
            "title",
            isPassword
                ? "Hide password"
                : "Show password"
        );

        passwordToggle.innerHTML =
            isPassword
                ? '<i data-lucide="eye-off"></i>'
                : '<i data-lucide="eye"></i>';

        if (window.lucide) {
            window.lucide.createIcons();
        }

    });

});