document.addEventListener("DOMContentLoaded", () => {
    const profileBtn = document.querySelector('.profile-btn');
    const profileDropdown = document.querySelector('.profile-dropdown');
    
    if (profileBtn && profileDropdown) {
        let isLoaded = false;
        
        profileBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const isVisible = profileDropdown.style.display === 'block';
            profileDropdown.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible && !isLoaded) {
                const token = localStorage.getItem('nutrix_token');
                if (!token) return;
                try {
                    const res = await fetch('http://127.0.0.1:8000/user/profile', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (res.ok) {
                        const data = await res.json();
                        document.querySelectorAll('.dropdown-name').forEach(el => el.innerText = data.name || 'Anonymous User');
                        document.querySelectorAll('.dropdown-email').forEach(el => el.innerText = data.email || '');
                        isLoaded = true;
                    } else {
                        document.querySelectorAll('.dropdown-name').forEach(el => el.innerText = 'Session Expired');
                    }
                } catch (e) {
                    console.error('Failed to load profile for dropdown', e);
                    document.querySelectorAll('.dropdown-name').forEach(el => el.innerText = 'Error Loading');
                }
            }
        });

        document.addEventListener('click', (e) => {
            if (!profileDropdown.contains(e.target) && !profileBtn.contains(e.target)) {
                profileDropdown.style.display = 'none';
            }
        });
    }

    // Attach logout functionality globally, regardless of profile dropdown presence
    const logoutBtns = document.querySelectorAll('.logout-btn');
    logoutBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('nutrix_token');
            
            // Also clear any Supabase session tokens
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('sb-') && key.endsWith('-auth-token')) {
                    localStorage.removeItem(key);
                }
            });

            window.location.href = 'index.html';
        });
    });
});
