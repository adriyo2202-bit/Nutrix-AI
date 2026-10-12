document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('nutrix_token');
    
    if (!token) {
        // Redirect to login if not authenticated
        window.location.href = 'index.html';
        return;
    }

    try {
        const res = await fetch('http://127.0.0.1:8000/user/profile', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (res.ok) {
            const data = await res.json();
            
            // Set real data
            const nameEl = document.getElementById('profile-name');
            const emailEl = document.getElementById('profile-email');
            const dateEl = document.getElementById('profile-date');
            
            nameEl.innerText = data.name || 'Anonymous User';
            emailEl.innerText = data.email;
            
            if (data.created_at) {
                const date = new Date(data.created_at);
                dateEl.innerText = `Member since ${date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}`;
            } else {
                dateEl.innerText = 'New Member';
            }
            
            // Animate them in
            gsap.fromTo([nameEl, emailEl, dateEl], 
                { y: 20, opacity: 0 }, 
                { y: 0, opacity: 1, duration: 0.8, stagger: 0.1, ease: "power2.out" }
            );

        } else {
            console.error("Failed to fetch profile");
            localStorage.removeItem('nutrix_token');
            window.location.href = 'index.html';
        }
    } catch (err) {
        console.error("Network error", err);
    }

    // Logout logic
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('nutrix_token');
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith('sb-') && key.endsWith('-auth-token')) {
                localStorage.removeItem(key);
            }
        });
        window.location.href = 'index.html';
    });
    
    // Feature card hover animation (tiny bounce)
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, { y: -5, duration: 0.3, ease: 'power1.out' });
        });
        card.addEventListener('mouseleave', () => {
            gsap.to(card, { y: 0, duration: 0.3, ease: 'power1.out' });
        });
    });
});
