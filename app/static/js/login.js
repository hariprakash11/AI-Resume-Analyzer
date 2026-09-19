document.addEventListener("DOMContentLoaded", () => {

    const passwordInput =
        document.getElementById("password");

    const passwordToggle =
        document.getElementById("passwordToggle");

    const passwordEyeIcon =
        document.getElementById("passwordEyeIcon");


    if (
        !passwordInput ||
        !passwordToggle ||
        !passwordEyeIcon
    ) {
        return;
    }


    passwordToggle.addEventListener("click", () => {

        const isHidden =
            passwordInput.type === "password";


        /* ---------------------------------------------
           SHOW / HIDE PASSWORD
        --------------------------------------------- */

        passwordInput.type =
            isHidden
                ? "text"
                : "password";


        /* ---------------------------------------------
           CHANGE ICON
        --------------------------------------------- */

        passwordEyeIcon.setAttribute(
            "data-lucide",
            isHidden
                ? "eye-off"
                : "eye"
        );


        /* ---------------------------------------------
           ACCESSIBILITY
        --------------------------------------------- */

        passwordToggle.setAttribute(
            "aria-label",
            isHidden
                ? "Hide password"
                : "Show password"
        );

        passwordToggle.setAttribute(
            "title",
            isHidden
                ? "Hide password"
                : "Show password"
        );

        passwordToggle.setAttribute(
            "aria-pressed",
            isHidden
                ? "true"
                : "false"
        );


        /* ---------------------------------------------
           REFRESH LUCIDE ICON
        --------------------------------------------- */

        lucide.createIcons();

    });

});