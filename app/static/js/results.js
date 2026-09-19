/* =====================================================
   RESULTS PAGE JAVASCRIPT
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* =================================================
       ATS SCORE GAUGE
    ================================================= */

    const scoreContainer =
        document.getElementById("atsScoreContainer");

    const scoreElement =
        document.getElementById("resultsAtsScore");

    const progressBar =
        document.querySelector(".results-progress-bar");


    if (scoreContainer && scoreElement && progressBar) {

        let score =
            parseFloat(
                scoreContainer.dataset.score
            );

        if (Number.isNaN(score)) {
            score = 0;
        }

        score = Math.max(
            0,
            Math.min(
                100,
                score
            )
        );


        /* ---------------------------------------------
           SVG CIRCLE
        --------------------------------------------- */

        const radius = 72;

        const circumference =
            2 * Math.PI * radius;


        progressBar.style.strokeDasharray =
            circumference;


        progressBar.style.strokeDashoffset =
            circumference;


        /* ---------------------------------------------
           SCORE ANIMATION
        --------------------------------------------- */

        let currentScore = 0;

        const duration = 1200;

        const startTime =
            performance.now();


        function animateScore(timestamp) {

            const elapsed =
                timestamp - startTime;

            const progress =
                Math.min(
                    elapsed / duration,
                    1
                );


            /*
             * Smooth ease-out animation
             */

            const easedProgress =
                1 -
                Math.pow(
                    1 - progress,
                    3
                );


            currentScore =
                score * easedProgress;


            scoreElement.textContent =
                `${Math.round(currentScore)}%`;


            const offset =
                circumference -
                (
                    circumference *
                    (currentScore / 100)
                );


            progressBar.style.strokeDashoffset =
                offset;


            if (progress < 1) {

                requestAnimationFrame(
                    animateScore
                );

            } else {

                scoreElement.textContent =
                    `${Math.round(score)}%`;

            }
        }


        /*
         * Start animation slightly after
         * page rendering.
         */

        requestAnimationFrame(
            animateScore
        );
    }


    /* =================================================
       SCORE BREAKDOWN BARS
    ================================================= */

    const scoreFills =
        document.querySelectorAll(
            ".score-card-fill"
        );


    scoreFills.forEach((fill, index) => {

        let width =
            parseFloat(
                fill.dataset.width
            );


        if (Number.isNaN(width)) {
            width = 0;
        }


        width =
            Math.max(
                0,
                Math.min(
                    100,
                    width
                )
            );


        /*
         * Make sure animation starts
         * from zero.
         */

        fill.style.width = "0%";


        /*
         * Stagger each card slightly.
         */

        const delay =
            150 + (index * 80);


        setTimeout(() => {

            requestAnimationFrame(() => {

                fill.style.width =
                    `${width}%`;

            });

        }, delay);

    });


    /* =================================================
       OPTIONAL SCORE CARD FADE-IN
    ================================================= */

    const scoreCards =
        document.querySelectorAll(
            ".score-card"
        );


    scoreCards.forEach(
        (card, index) => {

            card.style.opacity = "0";

            card.style.transform =
                "translateY(8px)";


            const delay =
                100 + (index * 80);


            setTimeout(() => {

                card.style.transition =
                    "opacity 0.45s ease, " +
                    "transform 0.45s ease";


                card.style.opacity = "1";

                card.style.transform =
                    "translateY(0)";

            }, delay);

        }
    );


    /* =================================================
       RECOMMENDATION CARDS
    ================================================= */

    const recommendationCards =
        document.querySelectorAll(
            ".recommendation-card"
        );


    recommendationCards.forEach(
        (card, index) => {

            card.style.opacity = "0";

            card.style.transform =
                "translateY(8px)";


            const delay =
                250 + (index * 70);


            setTimeout(() => {

                card.style.transition =
                    "opacity 0.45s ease, " +
                    "transform 0.45s ease";


                card.style.opacity = "1";

                card.style.transform =
                    "translateY(0)";

            }, delay);

        }
    );


    /* =================================================
       ACCESSIBILITY
    ================================================= */

    if (progressBar) {

        progressBar.setAttribute(
            "role",
            "progressbar"
        );


        progressBar.setAttribute(
            "aria-valuemin",
            "0"
        );


        progressBar.setAttribute(
            "aria-valuemax",
            "100"
        );


        const score =
            scoreContainer
                ? parseFloat(
                    scoreContainer.dataset.score
                )
                : 0;


        progressBar.setAttribute(
            "aria-valuenow",
            Math.round(
                Math.max(
                    0,
                    Math.min(
                        100,
                        score || 0
                    )
                )
            )
        );

    }


    /* =================================================
       REDUCE MOTION SUPPORT
    ================================================= */

    const prefersReducedMotion =
        window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;


    if (prefersReducedMotion) {

        /*
         * Instantly display everything
         * for users who prefer reduced motion.
         */

        if (
            scoreContainer &&
            scoreElement
        ) {

            let score =
                parseFloat(
                    scoreContainer.dataset.score
                );

            if (Number.isNaN(score)) {
                score = 0;
            }

            score =
                Math.max(
                    0,
                    Math.min(
                        100,
                        score
                    )
                );


            scoreElement.textContent =
                `${Math.round(score)}%`;
        }


        if (progressBar) {

            const radius = 72;

            const circumference =
                2 * Math.PI * radius;


            const score =
                scoreContainer
                    ? parseFloat(
                        scoreContainer.dataset.score
                    ) || 0
                    : 0;


            const clampedScore =
                Math.max(
                    0,
                    Math.min(
                        100,
                        score
                    )
                );


            progressBar.style.strokeDasharray =
                circumference;


            progressBar.style.strokeDashoffset =
                circumference -
                (
                    circumference *
                    clampedScore /
                    100
                );

        }


        scoreFills.forEach(
            (fill) => {

                let width =
                    parseFloat(
                        fill.dataset.width
                    ) || 0;


                width =
                    Math.max(
                        0,
                        Math.min(
                            100,
                            width
                        )
                    );


                fill.style.width =
                    `${width}%`;

            }
        );


        scoreCards.forEach(
            (card) => {

                card.style.opacity = "1";

                card.style.transform =
                    "none";

                card.style.transition =
                    "none";

            }
        );


        recommendationCards.forEach(
            (card) => {

                card.style.opacity = "1";

                card.style.transform =
                    "none";

                card.style.transition =
                    "none";

            }
        );

    }

});