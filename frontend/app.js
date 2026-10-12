const API_BASE = 'http://127.0.0.1:8000';
let token = '';

// Tab Switching Logic
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');

        const targetId = item.getAttribute('data-target');
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        document.getElementById(targetId).classList.add('active');
    });
});
function switchTab(id) {
    document.querySelector(`.nav-item[data-target="${id}"]`).click();
}

// Mock Workouts
const workouts = [
    { title: "Morning Run", desc: "45 mins • Outdoor", cal: "420 kcal", icon: "person-running" },
    { title: "HIIT Session", desc: "30 mins • Indoor", cal: "350 kcal", icon: "bolt" }
];
document.getElementById('workoutList').innerHTML = workouts.map(w => `
    <div style="display: flex; gap: 1rem; margin-bottom: 1rem; align-items: center;">
        <div style="width: 40px; height: 40px; border-radius: 10px; background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">
            <i class="fa-solid fa-${w.icon} text-gradient"></i>
        </div>
        <div style="flex: 1;">
            <div style="font-weight: 600;">${w.title}</div>
            <div style="font-size: 0.8rem; color: var(--text-muted);">${w.desc}</div>
        </div>
        <div style="font-weight: bold; color: var(--primary);">${w.cal}</div>
    </div>
`).join('');

// Authentication (Attempt Developer Login)
async function getAuthToken() {
    try {
        const formData = new URLSearchParams();
        formData.append('username', 'dev@cca.com');
        formData.append('password', 'CCA_WELCOMES');
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        if (res.ok) {
            const data = await res.json();
            token = data.access_token;
        }
    } catch (e) { console.warn("Dev login failed, API calls might be unauthorized."); }
}
getAuthToken();

// Diet Planner Logic
document.getElementById('dietForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    document.getElementById('planEmpty').classList.add('hidden');
    document.getElementById('planResult').classList.add('hidden');
    document.getElementById('planLoading').classList.remove('hidden');

    const payload = {
        age: parseInt(document.getElementById('age').value),
        height: parseFloat(document.getElementById('height').value),
        weight: parseFloat(document.getElementById('weight').value),
        goal: document.getElementById('goal').value,
        diet_type: document.getElementById('diet_type').value
    };

    try {
        const res = await fetch(`${API_BASE}/diet-plan`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        
        document.getElementById('planLoading').classList.add('hidden');
        document.getElementById('planResult').classList.remove('hidden');

        if (!res.ok) {
            document.getElementById('planResult').innerHTML = `<p style="color:var(--danger)">Error: ${data.detail || 'Failed to generate plan'}</p>`;
            return;
        }

        // Render Plan
        let html = `<h3>${data.title || 'Your Personalized Plan'}</h3>`;
        if (data.daily_plan) {
            data.daily_plan.forEach(meal => {
                html += `
                    <div class="plan-meal">
                        <h4>${meal.meal_type}</h4>
                        <p>${meal.suggestion}</p>
                    </div>
                `;
            });
        } else {
            html += `<pre style="white-space: pre-wrap; font-size: 0.9rem;">${JSON.stringify(data, null, 2)}</pre>`;
        }
        document.getElementById('planResult').innerHTML = html;

    } catch (err) {
        document.getElementById('planLoading').classList.add('hidden');
        document.getElementById('planResult').classList.remove('hidden');
        document.getElementById('planResult').innerHTML = `<p style="color:var(--danger)">Network Error: ${err.message}</p>`;
    }
});

// Scanner Logic
const fileInput = document.getElementById('labelImage');
const previewImg = document.getElementById('previewImg');
const scanPreview = document.getElementById('scanPreview');
const uploadZone = document.getElementById('uploadZone');

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        previewImg.src = URL.createObjectURL(e.target.files[0]);
        uploadZone.classList.add('hidden');
        scanPreview.classList.remove('hidden');
    }
});

document.getElementById('analyzeBtn').addEventListener('click', async () => {
    if (fileInput.files.length === 0) return;
    
    scanPreview.classList.add('hidden');
    document.getElementById('scanLoading').classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const res = await fetch(`${API_BASE}/analyze-label`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        const data = await res.json();
        document.getElementById('scanLoading').classList.add('hidden');
        
        const resultDiv = document.getElementById('scanResult');
        resultDiv.classList.remove('hidden');

        if (!res.ok) {
            resultDiv.innerHTML = `<p style="color:var(--danger)">Error: ${data.detail || 'Failed'}</p>`;
            return;
        }

        // Render Ingredients
        let ingHtml = data.ingredients.map(ing => {
            const cls = ing.safety_verdict === 'safe' ? 'safe' : (ing.safety_verdict === 'caution' ? 'caution' : 'unsafe');
            return `<span class="ingredient-badge ${cls}">${ing.name}</span>`;
        }).join('');

        resultDiv.innerHTML = `
            <div class="glass-card">
                <h3 style="display:flex; justify-content:space-between; align-items:center;">
                    Safety Score: 
                    <span style="font-size: 2rem; color: ${data.overall_safety_score > 70 ? 'var(--primary)' : 'var(--warning)'};">${data.overall_safety_score}/100</span>
                </h3>
                <p style="margin-bottom: 1rem; color: var(--text-muted);">${data.summary_bn_en || ''}</p>
                <div>${ingHtml}</div>
            </div>
        `;
    } catch (err) {
        document.getElementById('scanLoading').classList.add('hidden');
        document.getElementById('scanResult').classList.remove('hidden');
        document.getElementById('scanResult').innerHTML = `<p style="color:var(--danger)">Error: ${err.message}</p>`;
    }
});

// Chat Logic
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatMessages = document.getElementById('chatMessages');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // Add user message
    chatMessages.innerHTML += `
        <div class="message user">
            <div class="msg-bubble">${query}</div>
        </div>
    `;
    chatInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Add loading bubble
    const id = 'msg-' + Date.now();
    chatMessages.innerHTML += `
        <div class="message ai" id="${id}">
            <div class="msg-bubble"><div class="spinner" style="width:20px;height:20px;border-width:2px;margin:0;"></div></div>
        </div>
    `;
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify({ query })
        });

        const data = await res.json();
        const bubble = document.getElementById(id).querySelector('.msg-bubble');
        
        if (res.ok) {
            bubble.innerHTML = data.answer.replace(/\n/g, '<br>');
        } else {
            bubble.innerHTML = `<span style="color:var(--danger)">Error: ${data.detail || 'Failed'}</span>`;
        }
    } catch (err) {
        document.getElementById(id).querySelector('.msg-bubble').innerHTML = `<span style="color:var(--danger)">Network Error</span>`;
    }
    chatMessages.scrollTop = chatMessages.scrollHeight;
});
