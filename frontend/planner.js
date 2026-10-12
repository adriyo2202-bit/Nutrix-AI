document.addEventListener('DOMContentLoaded', () => {

    // --- UI Interactions ---
    const setupButtonGroup = (groupId) => {
        const group = document.getElementById(groupId);
        if (!group) return;
        const buttons = group.querySelectorAll('.select-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    };

    setupButtonGroup('gender-group');
    setupButtonGroup('goal-group');
    setupButtonGroup('diet-group');

    const getActiveValue = (groupId) => {
        const activeBtn = document.querySelector(`#${groupId} .select-btn.active`);
        return activeBtn ? activeBtn.getAttribute('data-val') : '';
    };

    const form = document.getElementById('diet-form');
    const formSection = document.getElementById('planner-form-section');
    const loadSection = document.getElementById('loading-section');
    const resultSection = document.getElementById('results-section');
    const resetBtn = document.getElementById('reset-btn');

    // --- Form Submission ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const height = parseFloat(document.getElementById('height').value);
        const weight = parseFloat(document.getElementById('weight').value);
        const age = parseInt(document.getElementById('age').value);
        const gender = getActiveValue('gender-group');
        const goal = getActiveValue('goal-group');
        const dietType = getActiveValue('diet-group');

        if (!height || !weight || !age) {
            alert("Please fill in all numerical fields.");
            return;
        }

        // Calculate BMI instantly
        const heightM = height / 100;
        const bmi = (weight / (heightM * heightM)).toFixed(1);

        let verdict = "Normal Weight";
        let color = "#4CAF50"; // Green
        if (bmi < 18.5) { verdict = "Underweight"; color = "#FFEB3B"; }
        else if (bmi >= 25 && bmi < 29.9) { verdict = "Overweight"; color = "#FF9800"; }
        else if (bmi >= 30) { verdict = "Obese"; color = "#F44336"; }

        // Setup BMI Gauge
        document.getElementById('bmi-number').innerText = bmi;
        document.getElementById('bmi-verdict').innerText = verdict;
        document.getElementById('bmi-verdict').style.color = color;

        // Map BMI (10 to 40) to gauge stroke-dashoffset (125 to 0)
        let normalizedBmi = Math.max(10, Math.min(40, bmi));
        let pct = (normalizedBmi - 10) / 30; // 0.0 to 1.0
        let offset = 125 - (pct * 125);
        document.getElementById('bmi-path').style.strokeDashoffset = offset;

        // Transition to Loading
        gsap.to(formSection, {
            opacity: 0, scale: 0.95, duration: 0.4, onComplete: () => {
                formSection.classList.add('hidden');
                loadSection.classList.remove('hidden');
                gsap.fromTo(loadSection, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4 });

                // Start Loading Animation
                startLoadingAnimation();
                fetchDietPlan(height, weight, age, goal, dietType);
            }
        });
    });

    // --- Loading Animation ---
    let progressTween;
    let textInterval;
    const progressFill = document.getElementById('progress-fill');
    const loadingPercentText = document.getElementById('loading-percent');
    const loadingMessage = document.getElementById('loading-message');

    function startLoadingAnimation() {
        let fakeProgress = { val: 0 };
        progressTween = gsap.to(fakeProgress, {
            val: 99,
            duration: 90, // Assume ~90 seconds for local 9B model
            ease: "power1.out",
            onUpdate: function () {
                loadingPercentText.innerText = Math.floor(fakeProgress.val) + '%';
                progressFill.style.width = fakeProgress.val + '%';
            }
        });

        const loadingTexts = [
            "Calculating Basal Metabolic Rate...",
            "Querying RAG database for regional Indian foods...",
            "Prompting Qwen3.5:9B AI Model for strict roadmap...",
            "Validating nutritional balance and macros...",
            "Finalizing your master plan..."
        ];

        let textIndex = 0;
        textInterval = setInterval(() => {
            textIndex = Math.min(textIndex + 1, loadingTexts.length - 1);
            loadingMessage.innerText = loadingTexts[textIndex];
        }, 6000);
    }

    // --- API Fetch ---
    async function fetchDietPlan(height, weight, age, goal, dietType) {
        try {
            // Get Token
            const token = localStorage.getItem('nutrix_token');
            if (!token) {
                throw new Error("You must be logged in to generate a diet plan.");
            }

            // Fetch Plan
            const reqBody = {
                age: age,
                height: height,
                weight: weight,
                goal: goal,
                diet_type: dietType
            };

            const planRes = await fetch('http://127.0.0.1:8000/diet-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(reqBody)
            });

            if (!planRes.ok) {
                const errorData = await planRes.json().catch(() => ({}));
                throw new Error(errorData.detail || errorData.error || "API failed");
            }

            const data = await planRes.json();
            if (data.error) throw new Error(data.error);

            renderResults(data);

        } catch (err) {
            alert("Failed to generate plan: " + err);
            progressTween.kill();
            clearInterval(textInterval);
            loadSection.classList.add('hidden');
            formSection.classList.remove('hidden');
            gsap.to(formSection, { opacity: 1, scale: 1, duration: 0.4 });
        }
    }

    // --- Render Results ---
    function renderResults(data) {
        progressTween.kill();
        clearInterval(textInterval);

        loadingPercentText.innerText = '100%';
        progressFill.style.width = '100%';

        setTimeout(() => {
            // Populate DOM
            document.getElementById('goal-alignment').innerText = '"' + (data.goal_alignment || "Follow this roadmap strictly to reach your goal.") + '"';

            document.getElementById('meal-breakfast').innerText = data.daily_roadmap?.breakfast || "Oats & Fruits";
            document.getElementById('meal-lunch').innerText = data.daily_roadmap?.lunch || "Chicken/Paneer Rice Bowl";
            document.getElementById('meal-snack').innerText = data.daily_roadmap?.snack || "Greek Yogurt / Nuts";
            document.getElementById('meal-dinner').innerText = data.daily_roadmap?.dinner || "Grilled Fish/Tofu with Veggies";

            const popList = (id, arr) => {
                const ul = document.getElementById(id);
                ul.innerHTML = '';
                if (arr && arr.length) {
                    arr.forEach(item => {
                        const li = document.createElement('li');
                        li.innerText = item;
                        ul.appendChild(li);
                    });
                }
            };

            popList('mandatory-fuel', data.mandatory_fuel);
            popList('forbidden-fuel', data.strictly_forbidden);

            // Hide loader, show results
            gsap.to(loadSection, {
                opacity: 0, y: -20, duration: 0.4, onComplete: () => {
                    loadSection.classList.add('hidden');
                    resultSection.classList.remove('hidden');
                    gsap.fromTo(resultSection, { opacity: 0, scale: 0.95 }, { opacity: 1, scale: 1, duration: 0.5, ease: "power2.out" });

                    // Animate elements inside
                    gsap.from(".results-top .glass-card", { y: 20, opacity: 0, duration: 0.5, stagger: 0.2, delay: 0.2 });
                    gsap.from(".meal-card", { y: 20, opacity: 0, duration: 0.5, stagger: 0.1, delay: 0.4 });
                    gsap.from(".rule-card", { y: 20, opacity: 0, duration: 0.5, stagger: 0.2, delay: 0.6 });
                }
            });
        }, 500);
    }

    // --- Reset ---
    resetBtn.addEventListener('click', () => {
        gsap.to(resultSection, {
            opacity: 0, scale: 0.95, duration: 0.4, onComplete: () => {
                resultSection.classList.add('hidden');
                formSection.classList.remove('hidden');
                gsap.fromTo(formSection, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4 });
            }
        });
    });
});
