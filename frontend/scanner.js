document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const scanLine = document.querySelector('.scan-line');
    
    // States
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const resultsData = document.getElementById('results-data');
    
    // Results Elements
    const scoreText = document.getElementById('score-text');
    const scoreCirclePath = document.getElementById('score-circle-path');
    const scoreLabel = document.getElementById('score-label');
    const scoreDesc = document.getElementById('score-desc');
    const aiSummaryText = document.getElementById('ai-summary-text');
    const safeUl = document.getElementById('safe-ul');
    const harmfulUl = document.getElementById('harmful-ul');
    const progressFill = document.querySelector('.progress-fill');

    // Mouse Glow
    const cursorGlow = document.getElementById('cursor-glow');
    window.addEventListener('mousemove', (e) => {
        gsap.to(cursorGlow, {
            x: e.clientX,
            y: e.clientY,
            duration: 0.8,
            ease: "power2.out"
        });
    });

    // Upload Handling
    uploadZone.addEventListener('click', () => fileInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length) {
            handleFile(this.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            // Show Image
            imagePreview.src = e.target.result;
            uploadZone.classList.add('hidden');
            previewContainer.classList.remove('hidden');

            // Start Mock Scan Process
            startScanProcess(file);
        };
        reader.readAsDataURL(file);
    }

    function startScanProcess(file) {
        // Change State
        emptyState.classList.add('hidden');
        resultsData.classList.add('hidden');
        loadingState.classList.remove('hidden');

        // Animate Scan Line over Image
        gsap.fromTo(scanLine, 
            { top: '0%' }, 
            { top: '100%', duration: 1.5, repeat: -1, yoyo: true, ease: "power1.inOut" }
        );

        // Smart LLM Loading Simulation
        // We know Ollama takes ~2.5 minutes, so we animate the bar and percentage slowly to 99%
        const loadingPercentText = document.getElementById('loading-percent');
        const loadingMessage = document.getElementById('loading-message');
        
        let fakeProgress = { val: 0 };
        gsap.to(progressFill, { width: '99%', duration: 150, ease: "power1.out" });
        const progressTween = gsap.to(fakeProgress, {
            val: 99,
            duration: 150,
            ease: "power1.out",
            onUpdate: function() {
                loadingPercentText.innerText = Math.floor(fakeProgress.val) + '%';
            }
        });

        // Change loading text dynamically based on the percentage
        const loadingTexts = [
            "Running YOLOv8 Object Detection...",
            "Extracting text via OCR Engine...",
            "Loading Qwen3.5:9B AI Model into Memory...",
            "Evaluating health risks and safety scores...",
            "Formatting EU and FSSAI safety verdicts...",
            "Finalizing dynamic RAG analysis..."
        ];
        
        let textIndex = 0;
        const textInterval = setInterval(() => {
            textIndex = Math.min(textIndex + 1, loadingTexts.length - 1);
            loadingMessage.innerText = loadingTexts[textIndex];
        }, 8000);

        const formData = new FormData();
        formData.append('file', fileInput.files[0] || file);

        // Fetch API Token
        fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'username=dev@cca.com&password=CCA_WELCOMES'
        })
        .then(res => res.json())
        .then(data => {
            const token = data.access_token;
            return fetch('http://127.0.0.1:8000/analyze-label', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
        })
        .then(async res => {
            if(!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "API Error");
            }
            return res.json();
        })
        .then(realData => {
            clearInterval(textInterval);
            progressTween.kill(); // Stop the fake progress
            
            // Jump to 100% instantly
            loadingPercentText.innerText = '100%';
            gsap.to(progressFill, { width: '100%', duration: 0.2 });
            
            setTimeout(() => {
                // Format the backend data into our UI structure
                const uiData = {
                    score: realData.overall_safety_score || 0,
                    summary: realData.summary_bn_en || "Analysis complete.",
                    safe: [],
                    harmful: []
                };

                const ingredients = realData.ingredients || [];
                ingredients.forEach(ing => {
                    if (ing.safety_verdict === 'safe') {
                        uiData.safe.push(ing.name);
                    } else {
                        uiData.harmful.push({
                            name: ing.name,
                            reason: ing.safety_reason || "Caution advised."
                        });
                    }
                });

                showResults(uiData);
            }, 400); // slight delay so they can see 100%
        })
        .catch(err => {
            clearInterval(textInterval);
            progressTween.kill();
            alert("Backend processing failed: " + err);
            // Fallback to empty if it fails
            gsap.killTweensOf(scanLine);
            loadingState.classList.add('hidden');
            emptyState.classList.remove('hidden');
        });
    }

    function showResults(data) {
        // Stop scanning animation
        gsap.killTweensOf(scanLine);
        scanLine.style.display = 'none';

        // Switch states
        loadingState.classList.add('hidden');
        resultsData.classList.remove('hidden');

        // Animate container in
        gsap.fromTo(resultsData, 
            { opacity: 0, y: 20 }, 
            { opacity: 1, y: 0, duration: 0.5 }
        );

        populateResults(data);
    }

    function populateResults(data) {
        // 1. Animate Score Circle
        const score = data.score;
        let color1 = "var(--green)";
        let color2 = "#059669"; // darker green
        let label = "GENERALLY SAFE";
        
        if (score < 70) { 
            color1 = "var(--orange)"; 
            color2 = "#d97706"; // darker orange
            label = "CONSUME WITH CAUTION"; 
        }
        if (score < 40) { 
            color1 = "var(--red)"; 
            color2 = "#991b1b"; // darker red
            label = "HARMFUL - AVOID"; 
        }

        // Update gradient colors
        document.getElementById('grad-start').setAttribute('stop-color', color1);
        document.getElementById('grad-end').setAttribute('stop-color', color2);
        
        scoreLabel.innerText = label;
        scoreLabel.style.background = `linear-gradient(90deg, ${color1}, ${color2})`;
        scoreLabel.style.webkitBackgroundClip = 'text';
        scoreLabel.style.webkitTextFillColor = 'transparent';
        
        // Dash array is out of 100
        setTimeout(() => {
            scoreCirclePath.setAttribute('stroke-dasharray', `${score}, 100`);
        }, 100);

        // Counter animation for text
        gsap.to({ val: 0 }, {
            val: score,
            duration: 1.5,
            ease: "power2.out",
            onUpdate: function() {
                scoreText.innerHTML = Math.floor(this.targets()[0].val);
            }
        });

        // 2. Summary
        aiSummaryText.innerHTML = data.summary;

        // 3. Populate Lists
        safeUl.innerHTML = '';
        data.safe.forEach(ing => {
            const li = document.createElement('li');
            li.innerHTML = `<span><i class="fa-solid fa-check" style="margin-right:8px; color:var(--green)"></i> ${ing}</span>`;
            safeUl.appendChild(li);
        });

        harmfulUl.innerHTML = '';
        data.harmful.forEach(ing => {
            const li = document.createElement('li');
            li.innerHTML = `<div>
                <strong><i class="fa-solid fa-triangle-exclamation" style="margin-right:8px; color:var(--red)"></i> ${ing.name}</strong>
                <span>${ing.reason}</span>
            </div>`;
            harmfulUl.appendChild(li);
        });

        // Stagger list items in
        gsap.fromTo(".ingredient-list li", 
            { opacity: 0, x: -10 },
            { opacity: 1, x: 0, duration: 0.4, stagger: 0.1, delay: 0.3 }
        );
    }

    // Reset Functionality
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            // Hide results
            resultsData.classList.add('hidden');
            previewContainer.classList.add('hidden');
            
            // Show upload zone
            uploadZone.classList.remove('hidden');
            emptyState.classList.remove('hidden');
            
            // Clear input
            fileInput.value = '';
            
            // Animate upload zone entrance
            gsap.fromTo(uploadZone, 
                { opacity: 0, scale: 0.95 },
                { opacity: 1, scale: 1, duration: 0.4, ease: "power2.out" }
            );
        });
    }
});
