document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       MOBILE NAVIGATION
    ===================================================== */

    const menuToggle = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (menuToggle && navLinks) {

        menuToggle.addEventListener("click", () => {

            navLinks.classList.toggle("active");

        });

    }


    /* =====================================================
       FILE SELECTION
    ===================================================== */

    const resumeInput = document.getElementById("resume");
    const selectedFile = document.getElementById("selected-file");

    if (resumeInput && selectedFile) {

        resumeInput.addEventListener("change", () => {

            if (resumeInput.files.length > 0) {

                const file = resumeInput.files[0];

                selectedFile.textContent =
                    file.name;

                selectedFile.classList.add("show");

            } else {

                selectedFile.textContent = "";

                selectedFile.classList.remove("show");

            }

        });

    }


    /* =====================================================
       HOME PAGE ATS PREVIEW GAUGE
    ===================================================== */

    const homeCircle =
        document.querySelector(".progress-bar");

    const homeScore =
        document.getElementById("atsScore");

    if (homeCircle && homeScore) {

        const radius = 72;

        const circumference =
            2 * Math.PI * radius;

        homeCircle.style.strokeDasharray =
            circumference;

        homeCircle.style.strokeDashoffset =
            circumference;


        let current = 0;

        const target = 92;

        const interval = setInterval(() => {

            current++;

            if (current >= target) {

                current = target;

                clearInterval(interval);

            }


            const percentage =
                current / 100;


            const offset =
                circumference -
                (percentage * circumference);


            homeCircle.style.strokeDashoffset =
                offset;


            homeScore.innerText =
                current + "%";


        }, 20);

    }


    /* =====================================================
       RESULTS ATS GAUGE
    ===================================================== */

    const circle = document.querySelector(
        ".results-progress-bar"
    );

    const scoreElement = document.getElementById(
        "resultsAtsScore"
    );

    if (!circle || !scoreElement) {
        return;
    }


    const radius = 72;

    const circumference =
        2 * Math.PI * radius;


    circle.style.strokeDasharray =
        circumference;


    circle.style.strokeDashoffset =
        circumference;


    let target =
        Number(window.ATS_SCORE || 0);


    target = Math.max(
        0,
        Math.min(100, target)
    );


    let current = 0;


    const duration = 1500;

    const steps = 60;

    const increment =
        target / steps;

    const intervalTime =
        duration / steps;


    const interval = setInterval(() => {

        current += increment;


        if (current >= target) {

            current = target;

            clearInterval(interval);
        }


        const percentage =
            current / 100;


        const offset =
            circumference -
            (percentage * circumference);


        circle.style.strokeDashoffset =
            offset;


        scoreElement.innerText =
            Math.round(current) + "%";


    }, intervalTime);

});