
document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // LOAD GAME QUESTIONS FROM HTML JSON DATA
    // =========================================================

    const gameDataElement =
        document.getElementById("game-data");

    if (!gameDataElement) {
        console.error("Game data was not found.");
        return;
    }

    let questions;

    try {
        questions = JSON.parse(
            gameDataElement.textContent
        );
    } catch (error) {
        console.error(
            "Could not load game questions:",
            error
        );
        return;
    }


    // =========================================================
    // GAME VARIABLES
    // =========================================================

    let currentQuestion = 0;
    let score = 0;
    let answered = false;
    let scoreSaved = false;


    // =========================================================
    // HTML ELEMENTS
    // =========================================================

    const questionText =
        document.getElementById("question-text");

    const choicesContainer =
        document.getElementById("choices-container");

    const explanation =
        document.getElementById("explanation");

    const nextButton =
        document.getElementById("next-button");

    const scoreDisplay =
        document.getElementById("score-display");

    const questionNumber =
        document.getElementById("question-number");

    const currentNumber =
        document.getElementById("current-number");

    const progressBar =
        document.getElementById("game-progress-bar");

    const questionCard =
        document.getElementById("question-card");

    const gameResult =
        document.getElementById("game-result");

    const finalScore =
        document.getElementById("final-score");

    const restartButton =
        document.getElementById("restart-button");


    // =========================================================
    // GET GAME ID
    // =========================================================

    const gamePage =
        document.querySelector(
            ".game-play-page"
        );

    const gameId =
        gamePage
            ? gamePage.dataset.gameId
            : null;


    if (!gameId) {
        console.error(
            "Game ID was not found."
        );
        return;
    }


    // =========================================================
    // CHECK REQUIRED ELEMENTS
    // =========================================================

    if (
        !questionText ||
        !choicesContainer ||
        !explanation ||
        !nextButton ||
        !scoreDisplay ||
        !questionNumber ||
        !currentNumber ||
        !progressBar ||
        !questionCard ||
        !gameResult ||
        !finalScore ||
        !restartButton
    ) {
        console.error(
            "One or more game elements are missing from the page."
        );
        return;
    }


    // =========================================================
    // LOAD QUESTION
    // =========================================================

    function loadQuestion() {

        answered = false;

        const question =
            questions[currentQuestion];


        // -----------------------------------------------------
        // Question text
        // -----------------------------------------------------

        questionText.textContent =
            question.question;


        // -----------------------------------------------------
        // Question number
        // -----------------------------------------------------

        currentNumber.textContent =
            currentQuestion + 1;


        questionNumber.textContent =
            `Question ${currentQuestion + 1} of ${questions.length}`;


        // -----------------------------------------------------
        // Score
        // -----------------------------------------------------

        scoreDisplay.textContent =
            `⭐ Score: ${score}`;


        // -----------------------------------------------------
        // Progress
        // -----------------------------------------------------

        const progress =
            (currentQuestion / questions.length) * 100;

        progressBar.style.width =
            `${progress}%`;


        // -----------------------------------------------------
        // Clear previous choices
        // -----------------------------------------------------

        choicesContainer.innerHTML = "";


        // -----------------------------------------------------
        // Hide explanation
        // -----------------------------------------------------

        explanation.classList.add(
            "hidden"
        );

        explanation.textContent = "";


        // -----------------------------------------------------
        // Hide next button
        // -----------------------------------------------------

        nextButton.classList.add(
            "hidden"
        );


        // -----------------------------------------------------
        // Create answer buttons
        // -----------------------------------------------------

        question.choices.forEach(
            function (choice, index) {

                const button =
                    document.createElement("button");


                button.type =
                    "button";


                button.className =
                    "choice-button";


                button.textContent =
                    choice;


                button.addEventListener(
                    "click",
                    function () {

                        answerQuestion(
                            index,
                            button
                        );

                    }
                );


                choicesContainer.appendChild(
                    button
                );

            }
        );

    }


    // =========================================================
    // ANSWER QUESTION
    // =========================================================

    function answerQuestion(
        selectedIndex,
        selectedButton
    ) {

        // Prevent answering twice
        if (answered) {
            return;
        }

        answered = true;


        const question =
            questions[currentQuestion];


        const buttons =
            document.querySelectorAll(
                ".choice-button"
            );


        // -----------------------------------------------------
        // Disable all choices
        // -----------------------------------------------------

        buttons.forEach(
            function (button) {

                button.disabled = true;

            }
        );


        // =====================================================
        // CORRECT ANSWER
        // =====================================================

        if (
            selectedIndex ===
            question.answer
        ) {

            score += 10;


            selectedButton.classList.add(
                "correct"
            );


            explanation.textContent =
                "✅ Correct! " +
                question.explanation;

        }


        // =====================================================
        // WRONG ANSWER
        // =====================================================

        else {

            selectedButton.classList.add(
                "incorrect"
            );


            // Highlight correct answer
            if (buttons[question.answer]) {

                buttons[
                    question.answer
                ].classList.add(
                    "correct"
                );

            }


            explanation.textContent =
                "💡 Not quite. " +
                question.explanation;

        }


        // -----------------------------------------------------
        // Update score
        // -----------------------------------------------------

        scoreDisplay.textContent =
            `⭐ Score: ${score}`;


        // -----------------------------------------------------
        // Show explanation
        // -----------------------------------------------------

        explanation.classList.remove(
            "hidden"
        );


        // -----------------------------------------------------
        // Show next button
        // -----------------------------------------------------

        nextButton.classList.remove(
            "hidden"
        );

    }


    // =========================================================
    // NEXT QUESTION
    // =========================================================

    nextButton.addEventListener(
        "click",
        function () {

            currentQuestion++;


            if (
                currentQuestion >=
                questions.length
            ) {

                finishGame();

                return;

            }


            loadQuestion();

        }
    );


    // =========================================================
    // SAVE SCORE TO SERVER
    // =========================================================

    async function saveScore() {

        if (scoreSaved) {
            return;
        }


        scoreSaved = true;


        try {

            const response =
                await fetch(
                    `/games/api/${encodeURIComponent(gameId)}/score`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            score: score
                        })
                    }
                );


            const data =
                await response.json();


            // -------------------------------------------------
            // Server rejected the score
            // -------------------------------------------------

            if (!response.ok || !data.success) {

                console.error(
                    "Score could not be saved:",
                    data.message
                );

                showSaveMessage(
                    "⚠️ Your score could not be saved. Please try again.",
                    "error"
                );

                scoreSaved = false;

                return;

            }


            // -------------------------------------------------
            // Successful save
            // -------------------------------------------------

            showSaveMessage(
                `✅ Score saved! You earned ${data.earned_points} leaderboard points.`,
                "success"
            );


        } catch (error) {

            console.error(
                "Error saving score:",
                error
            );


            showSaveMessage(
                "⚠️ We could not connect to the server to save your score.",
                "error"
            );


            scoreSaved = false;

        }

    }


    // =========================================================
    // SHOW SAVE MESSAGE
    // =========================================================

    function showSaveMessage(
        message,
        type
    ) {

        let saveMessage =
            document.getElementById(
                "score-save-message"
            );


        // Create message if it does not exist
        if (!saveMessage) {

            saveMessage =
                document.createElement(
                    "div"
                );

            saveMessage.id =
                "score-save-message";


            saveMessage.style.marginTop =
                "18px";


            saveMessage.style.padding =
                "14px 16px";


            saveMessage.style.borderRadius =
                "12px";


            saveMessage.style.fontWeight =
                "600";


            gameResult.appendChild(
                saveMessage
            );

        }


        saveMessage.textContent =
            message;


        if (type === "success") {

            saveMessage.style.background =
                "rgba(81, 207, 102, 0.12)";

            saveMessage.style.border =
                "1px solid rgba(81, 207, 102, 0.25)";

            saveMessage.style.color =
                "var(--success)";

        } else {

            saveMessage.style.background =
                "rgba(255, 107, 107, 0.12)";

            saveMessage.style.border =
                "1px solid rgba(255, 107, 107, 0.25)";

            saveMessage.style.color =
                "var(--danger)";

        }

    }


    // =========================================================
    // FINISH GAME
    // =========================================================

    async function finishGame() {

        questionCard.classList.add(
            "hidden"
        );


        gameResult.classList.remove(
            "hidden"
        );


        const maximumScore =
            questions.length * 10;


        finalScore.textContent =
            `${score} / ${maximumScore}`;


        progressBar.style.width =
            "100%";


        // -----------------------------------------------------
        // Save score
        // -----------------------------------------------------

        await saveScore();

    }


    // =========================================================
    // RESTART GAME
    // =========================================================

    restartButton.addEventListener(
        "click",
        function () {

            currentQuestion = 0;

            score = 0;

            answered = false;

            scoreSaved = false;


            questionCard.classList.remove(
                "hidden"
            );


            gameResult.classList.add(
                "hidden"
            );


            loadQuestion();

        }
    );


    // =========================================================
    // START GAME
    // =========================================================

    loadQuestion();

});

