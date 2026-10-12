document.addEventListener('DOMContentLoaded', () => {
    const room = document.getElementById('room');
    const pullChain = document.getElementById('pullChain');
    const loginForm = document.getElementById('loginForm');
    const signInBtn = document.getElementById('signInBtn');
    const loginCard = document.getElementById('loginCard');
    const screenFlash = document.getElementById('screenFlash');

    let isLightOn = true; // Ends up ON after intro
    let isIntroPlaying = true; // Block interaction during intro
    let isLogin = true; // Track auth mode state globally

    // --- 1. 3D Card Hover Effect ---
    document.addEventListener('mousemove', (e) => {
        if (isIntroPlaying) return;
        
        // Only apply if we're hovering over the half where the card is
        if (isLogin && e.clientX < window.innerWidth / 2) return;
        if (!isLogin && e.clientX > window.innerWidth / 2) return;
        
        const rect = loginCard.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = ((y - centerY) / centerY) * -10; // Max 10 deg
        const rotateY = ((x - centerX) / centerX) * 10;
        
        gsap.to(loginCard, {
            rotationX: rotateX,
            rotationY: rotateY,
            transformPerspective: 1200,
            ease: 'power1.out',
            duration: 0.5
        });
    });

    document.addEventListener('mouseleave', () => {
        gsap.to(loginCard, { rotationX: 0, rotationY: 0, duration: 1, ease: 'elastic.out(1, 0.3)' });
    });


    // --- 2. Three.js Particle System ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('webgl-container').appendChild(renderer.domElement);

    // Create glowing particles (fireflies)
    const particleCount = 150;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const targetPositions = new Float32Array(particleCount * 3);
    const velocities = [];

    for(let i = 0; i < particleCount * 3; i+=3) {
        // Initial state: spread across screen
        positions[i] = (Math.random() - 0.5) * 40;     
        positions[i+1] = (Math.random() - 0.5) * 20;   
        positions[i+2] = (Math.random() - 0.5) * 30 - 10; 
        
        velocities.push({
            x: (Math.random() - 0.5) * 0.02,
            y: (Math.random() - 0.5) * 0.02,
            z: (Math.random() - 0.5) * 0.02
        });
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    // Custom glowing material
    const material = new THREE.PointsMaterial({
        color: 0xfacc15,
        size: 0.15,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);


    camera.position.z = 5;

    // Add subtle ambient floating 3D geometry to fill the "khali khali" corners
    const objectGroup = new THREE.Group();
    scene.add(objectGroup);

    const geo1 = new THREE.IcosahedronGeometry(1.5, 0);
    const geo2 = new THREE.TorusGeometry(2, 0.4, 16, 50);
    const geo3 = new THREE.OctahedronGeometry(1.8, 0);
    
    const matGeo = new THREE.MeshBasicMaterial({
        color: 0xfacc15,
        wireframe: true,
        transparent: true,
        opacity: 0.05 // Very subtle
    });

    const geometries = [geo1, geo2, geo3];
    const abstractMeshes = [];

    for(let i=0; i<12; i++) {
        const mesh = new THREE.Mesh(geometries[Math.floor(Math.random() * geometries.length)], matGeo);
        
        // Spread them towards the edges/corners
        mesh.position.set(
            (Math.random() - 0.5) * 50,
            (Math.random() - 0.5) * 30,
            (Math.random() - 0.5) * 20 - 15
        );
        mesh.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, 0);
        
        mesh.userData = {
            rx: (Math.random() - 0.5) * 0.005,
            ry: (Math.random() - 0.5) * 0.005,
            rz: (Math.random() - 0.5) * 0.005,
            floatY: (Math.random() - 0.5) * 0.01
        };
        
        objectGroup.add(mesh);
        abstractMeshes.push(mesh);
    }
    // --- 0.5. Initial State & Cinematic Netflix Intro ---
    matGeo.opacity = 0.05;
    material.opacity = 0.8;
    
    const splashScreen = document.getElementById('splash-screen');
    const splashText = document.querySelector('.splash-text');
    const startOverlay = document.getElementById('start-overlay');
    const startBtn = document.getElementById('start-btn');
    
    let introPhase = 'idle'; // 'idle', 'flowLeft', 'coalesce', 'none'

    function playAudioSequence() {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        const audioCtx = new AudioContext();
        if(audioCtx.state === 'suspended') audioCtx.resume();
        const t = audioCtx.currentTime;
        
        // Heartbeat Thump Function
        function thump(time) {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(65, time); // Deep bass
            osc.frequency.exponentialRampToValueAtTime(35, time + 0.3);
            gain.gain.setValueAtTime(0, time);
            gain.gain.linearRampToValueAtTime(2.0, time + 0.05); // Quick punch
            gain.gain.exponentialRampToValueAtTime(0.01, time + 0.3);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(time);
            osc.stop(time + 0.4);
        }

        // Duuuk... Duuuk (Heartbeats)
        thump(t);
        thump(t + 0.35); // 1st heartbeat
        
        thump(t + 1.2);
        thump(t + 1.55); // 2nd heartbeat

        // Cinematic Impact exactly when text zooms (at t + 2.5s)
        const impactTime = t + 2.5;
        const osc2 = audioCtx.createOscillator();
        const gain2 = audioCtx.createGain();
        osc2.type = 'triangle';
        osc2.frequency.setValueAtTime(100, impactTime);
        osc2.frequency.exponentialRampToValueAtTime(20, impactTime + 1.5);
        gain2.gain.setValueAtTime(0, impactTime);
        gain2.gain.linearRampToValueAtTime(1.5, impactTime + 0.1);
        gain2.gain.exponentialRampToValueAtTime(0.01, impactTime + 2.0);
        osc2.connect(gain2);
        gain2.connect(audioCtx.destination);
        osc2.start(impactTime);
        osc2.stop(impactTime + 2.0);
        
        // Noise Sweep/Whoosh at impact
        const bufferSize = audioCtx.sampleRate * 2;
        const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
        
        const noise = audioCtx.createBufferSource();
        noise.buffer = buffer;
        const noiseFilter = audioCtx.createBiquadFilter();
        noiseFilter.type = 'lowpass';
        noiseFilter.frequency.setValueAtTime(2000, impactTime);
        noiseFilter.frequency.exponentialRampToValueAtTime(100, impactTime + 1.5);
        
        const noiseGain = audioCtx.createGain();
        noiseGain.gain.setValueAtTime(0, impactTime);
        noiseGain.gain.linearRampToValueAtTime(0.4, impactTime + 0.1);
        noiseGain.gain.exponentialRampToValueAtTime(0.01, impactTime + 2.0);
        
        noise.connect(noiseFilter);
        noiseFilter.connect(noiseGain);
        noiseGain.connect(audioCtx.destination);
        noise.start(impactTime);
        noise.stop(impactTime + 2.0);
    }

    startBtn.addEventListener('click', () => {
        // 1. Enter button flies off to the left
        gsap.to(startBtn, { x: -window.innerWidth, opacity: 0, duration: 1, ease: "power2.in" });
        
        // Fade out overlay background slowly
        gsap.to(startOverlay, { backgroundColor: "rgba(0,0,0,0)", duration: 1, delay: 0.5, onComplete: () => {
            startOverlay.style.display = 'none';
        }});
        
        playAudioSequence(); // Play Heartbeats + Impact

        // 2. ThreeJS Particles flow left following the button
        introPhase = 'flowLeft';
        for(let i = 0; i < particleCount; i++) {
            velocities[i].x = -1 - Math.random() * 2; // Strong pull to the left
        }

        // 3. Coalesce particles to center and form text
        setTimeout(() => {
            introPhase = 'coalesce';
            const posAttr = particles.geometry.attributes.position.array;
            
            for(let i = 0; i < particleCount; i++) {
                gsap.to(velocities[i], { x: 0, y: 0, z: 0, duration: 1.5 });
                gsap.to(posAttr, {
                    [i*3]: (Math.random()-0.5)*5,     // tight cluster x
                    [i*3+1]: (Math.random()-0.5)*2,   // tight cluster y
                    [i*3+2]: (Math.random()-0.5)*5,   // tight cluster z
                    duration: 1.5,
                    ease: "power2.inOut",
                    onUpdate: () => { particles.geometry.attributes.position.needsUpdate = true; }
                });
            }

            // Text forms from a highly blurred, scattered state
            gsap.set(splashText, { x: 0, letterSpacing: "40px", opacity: 0, scale: 2, filter: "blur(20px)" });
            
            const splashTl = gsap.timeline();
            
            // 4. Form the text from the blur (happens over 1.5s as particles coalesce)
            splashTl.to(splashText, { letterSpacing: "5px", opacity: 1, scale: 1, filter: "blur(0px)", duration: 1.5, ease: "power2.out" })
                    // 5. The massive zoom in (happens at exactly 2.5s total time, aligned with audio drop)
                    .to(splashText, { scale: 20, opacity: 0, filter: "blur(10px)", duration: 0.8, ease: "power4.in" })
                    .to(splashScreen, { opacity: 0, duration: 0.3 }, "-=0.3")
                    .add(() => {
                        introPhase = 'none';
                        isIntroPlaying = false;
                        splashScreen.style.display = 'none';
                        
                        // Explode particles back out to their wide positions
                        for(let i = 0; i < particleCount; i++) {
                            velocities[i].x = (Math.random() - 0.5) * 0.02;
                            velocities[i].y = (Math.random() - 0.5) * 0.02;
                            velocities[i].z = (Math.random() - 0.5) * 0.02;
                            
                            gsap.to(posAttr, {
                                [i*3]: (Math.random() - 0.5) * 40,
                                [i*3+1]: (Math.random() - 0.5) * 20,
                                [i*3+2]: (Math.random() - 0.5) * 30 - 10,
                                duration: 2, ease: "expo.out",
                                onUpdate: () => { particles.geometry.attributes.position.needsUpdate = true; }
                            });
                        }

                        // Show the room & turn lamp on magically
                        room.classList.remove('off');
                        loginCard.classList.add('visible');
                    });
        }, 1000); // 1 second after click
    });

    // Animation Loop

    function animate() {
        requestAnimationFrame(animate);
        
        const positions = particles.geometry.attributes.position.array;
        
        for(let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            
            if (introPhase === 'warp') {
                // Warp effect: particles fly towards camera
                positions[i3+2] += 0.5;
                if(positions[i3+2] > 5) positions[i3+2] = -30;
            } else if (introPhase === 'idle' || introPhase === 'flowLeft' || introPhase === 'none') {
                // Apply velocities
                positions[i3] += velocities[i].x;
                positions[i3+1] += velocities[i].y;
                positions[i3+2] += velocities[i].z;
                
                // If flowing left, wrap particles if they go too far left
                if (introPhase === 'flowLeft' && positions[i3] < -20) {
                    positions[i3] = 20; // wrap to right
                }
            }

            // Normal bouncing off boundaries only when intro is over
            if (introPhase === 'none') {
                if(Math.abs(positions[i3]) > 20) velocities[i].x *= -1;
                if(Math.abs(positions[i3+1]) > 10) velocities[i].y *= -1;
                if(Math.abs(positions[i3+2] + 10) > 15) velocities[i].z *= -1;
            }
        }
        
        particles.geometry.attributes.position.needsUpdate = true;
        
        if (introPhase !== 'warp' && introPhase !== 'flowLeft') {
            particles.rotation.y += 0.001;
            
            // Slowly rotate floating geometries
            abstractMeshes.forEach(mesh => {
                mesh.rotation.x += mesh.userData.rx;
                mesh.rotation.y += mesh.userData.ry;
                mesh.rotation.z += mesh.userData.rz;
                mesh.position.y += mesh.userData.floatY;
                
                // Gentle bobbing boundary
                if(Math.abs(mesh.position.y) > 20) {
                    mesh.userData.floatY *= -1;
                }
            });
        }

        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // --- 3. Pull Chain Interaction ---
    pullChain.addEventListener('click', () => {
        if (isIntroPlaying) return;
        
        // NORMAL TOGGLE
        isLightOn = !isLightOn;
        room.classList.toggle('off');
        
        gsap.timeline()
            .to("#pullChain", { y: 25, duration: 0.1, ease: "power1.in" })
            .to("#pullChain", { y: 0, duration: 0.7, ease: "elastic.out(1.2, 0.2)" });

        gsap.to(material, {
            opacity: isLightOn ? 0.8 : 0.1,
            duration: 1.5,
            ease: "power2.inOut"
        });
        
        gsap.to(matGeo, {
            opacity: isLightOn ? 0.05 : 0.01,
            duration: 1.5,
            ease: "power2.inOut"
        });
    });

    // --- 4. Login & Sign Up Logic ---
    function playSuccessWarp() {
        // Trigger 3D Warp Animation
        introPhase = 'warp';
        
        // Stretch particles
        gsap.to(material, { size: 0.5, duration: 1 });
        
        // Hide UI elements smoothly
        gsap.to('.lamp-container', { opacity: 0, x: isLogin ? -100 : 100, duration: 1, ease: 'power2.in' });
        gsap.to(loginCard, { opacity: 0, x: isLogin ? 100 : -100, scale: 0.8, duration: 1, ease: 'power2.in' });
        
        // Flash screen white before redirect
        gsap.to(screenFlash, {
            opacity: 1,
            delay: 0.8,
            duration: 0.5,
            onComplete: () => {
                window.location.href = 'dashboard.html';
            }
        });
    }

    const supabaseUrl = 'https://cyarpuawppwwnzocorco.supabase.co';
    const supabaseKey = 'sb_publishable_6i2el78jez3trg8Up2xMsw_JI9h_nNr';
    let supabase = null;
    try {
        if (window.supabase) {
            supabase = window.supabase.createClient(supabaseUrl, supabaseKey);
        }
    } catch(e) {
        console.warn("Supabase init failed:", e);
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const fullname = document.getElementById('fullname').value;
        
        signInBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';
        signInBtn.disabled = true;

        if (!isLogin) {
            let useFallback = true;
            if (supabase) {
                try {
                    const { data, error } = await supabase.auth.signUp({
                        email: username,
                        password: password,
                        options: { data: { full_name: fullname } }
                    });
                    
                    if (!error && data.session) {
                        localStorage.setItem('nutrix_token', data.session.access_token);
                        signInBtn.innerHTML = 'Account Created!';
                        setTimeout(() => playSuccessWarp(), 1000);
                        useFallback = false;
                    } else if (!error && data.user) {
                        signInBtn.innerHTML = 'Check email to confirm!';
                        setTimeout(() => {
                            signInBtn.innerHTML = '<span class="btn-text">Sign Up</span><div class="btn-glow"></div>';
                            signInBtn.disabled = false;
                            signInBtn.style.backgroundColor = 'var(--accent)';
                        }, 3000);
                        useFallback = false;
                    }
                } catch(err) {
                    console.error("Supabase signup error:", err);
                }
            }

            if (useFallback) {
                try {
                    const res = await fetch('http://127.0.0.1:8000/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: username, password: password, name: fullname })
                    });
                    
                    if (res.ok) {
                        signInBtn.innerHTML = 'Account Created!';
                        // Automatically log them in now
                        const formData = new URLSearchParams();
                        formData.append('username', username);
                        formData.append('password', password);
                        const loginRes = await fetch('http://127.0.0.1:8000/login', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            body: formData
                        });
                        if (loginRes.ok) {
                            const data = await loginRes.json();
                            localStorage.setItem('nutrix_token', data.access_token);
                        }
                        setTimeout(() => playSuccessWarp(), 1000);
                    } else {
                        const err = await res.json();
                        signInBtn.innerHTML = err.detail || 'Error creating account';
                        signInBtn.style.backgroundColor = '#ef4444';
                        setTimeout(() => {
                            signInBtn.innerHTML = '<span class="btn-text">Sign Up</span><div class="btn-glow"></div>';
                            signInBtn.disabled = false;
                            signInBtn.style.backgroundColor = 'var(--accent)';
                        }, 2000);
                    }
                } catch (error) {
                    console.error(error);
                    signInBtn.innerHTML = '<span class="btn-text">Sign Up</span>';
                    signInBtn.disabled = false;
                }
            }
            return;
        }

        let useLoginFallback = true;
        if (supabase) {
            try {
                const { data, error } = await supabase.auth.signInWithPassword({
                    email: username,
                    password: password,
                });
                if (!error && data.session) {
                    localStorage.setItem('nutrix_token', data.session.access_token);
                    signInBtn.innerHTML = 'Welcome!';
                    playSuccessWarp();
                    useLoginFallback = false;
                }
            } catch(err) {
                console.error("Supabase login error:", err);
            }
        }

        if (useLoginFallback) {
            try {
                const formData = new URLSearchParams();
                formData.append('username', username);
                formData.append('password', password);
                
                const res = await fetch('http://127.0.0.1:8000/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });

                if (res.ok) {
                    const data = await res.json();
                    localStorage.setItem('nutrix_token', data.access_token);
                    signInBtn.innerHTML = 'Welcome!';
                    playSuccessWarp();
                } else {
                    signInBtn.innerHTML = 'Invalid Credentials';
                    signInBtn.style.backgroundColor = '#ef4444';
                    
                    // Shake effect on error
                    gsap.to(loginCard, {
                        x: isLogin ? () => (Math.random() - 0.5) * 20 : () => -window.innerWidth*0.35 + (Math.random() - 0.5) * 20,
                        y: () => (Math.random() - 0.5) * 20,
                        duration: 0.05,
                        yoyo: true,
                        repeat: 5,
                        onComplete: () => gsap.to(loginCard, {x: isLogin ? 0 : -window.innerWidth*0.35, y: 0, duration: 0.1})
                    });
                    
                    setTimeout(() => {
                        signInBtn.innerHTML = '<span class="btn-text">Sign In</span><div class="btn-glow"></div>';
                        signInBtn.disabled = false;
                        signInBtn.style.backgroundColor = 'var(--accent)';
                    }, 2000);
                }
            } catch (error) {
                console.error(error);
                signInBtn.innerHTML = '<span class="btn-text">Sign In</span>';
                signInBtn.disabled = false;
            }
        }
    });

    // --- 5. Sign Up Switch Animation ---
    const toggleAuthMode = document.getElementById('toggleAuthMode');
    
    toggleAuthMode.addEventListener('click', (e) => {
        e.preventDefault();
        isLogin = !isLogin;
        
        // Animate the text fade out & in
        gsap.to([".login-card h2", ".login-card p", ".btn-text"], {
            opacity: 0, duration: 0.3, onComplete: () => {
                document.querySelector('.login-card h2').innerText = isLogin ? "Welcome Back" : "Create Account";
                document.querySelector('.login-card p').innerText = isLogin ? "Enter your details to access your account" : "Join Nutrix AI for a healthier lifestyle";
                document.querySelector('.btn-text').innerText = isLogin ? "Sign In" : "Sign Up";
                toggleAuthMode.innerText = isLogin ? "Sign Up" : "Sign In";
                document.getElementById('switchText').firstChild.textContent = isLogin ? "Don't have an account? " : "Already have an account? ";
                
                gsap.to([".login-card h2", ".login-card p", ".btn-text"], { opacity: 1, duration: 0.3 });
            }
        });

        // Toggle sign up fields (Full Name)
        const signupFields = document.querySelectorAll('.signup-only');
        if (!isLogin) {
            signupFields.forEach(field => {
                field.style.display = 'flex';
                gsap.to(field, { height: '56px', opacity: 1, duration: 0.5, ease: "power2.out", marginTop: "1rem" });
            });
            document.getElementById('fullname').required = true;
        } else {
            signupFields.forEach(field => {
                gsap.to(field, { height: '0px', opacity: 0, marginTop: "0rem", duration: 0.3, ease: "power2.in", onComplete: () => {
                    field.style.display = 'none';
                }});
            });
            document.getElementById('fullname').required = false;
        }
        
        // 3D Morph Animation for Lamp & Card position swap
        if(!isLogin) {
            // Shift Lamp to Right, Make Smaller
            gsap.to(".lamp-container", { x: window.innerWidth * 0.35, scale: 0.6, duration: 1.8, ease: "power4.inOut" });
            // Light comes together (narrow beam)
            gsap.to(".light-beam", { clipPath: "polygon(48% 0, 52% 0, 80% 100%, 20% 100%)", filter: "blur(4px)", duration: 1.8, ease: "power4.inOut" });
            // Floor glow smaller
            gsap.to(".floor-glow", { width: 400, opacity: 0.5, duration: 1.8, ease: "power4.inOut" });
            // Shift Card to Left
            gsap.to(".login-wrapper", { x: -window.innerWidth * 0.35, duration: 1.8, ease: "power4.inOut" });
            
            // Background 3D Animation: Shift to Cool Cyan & Swirl Particles Left/Up
            gsap.to(material.color, { r: 0.0, g: 0.8, b: 1.0, duration: 1.8 }); 
            gsap.to(matGeo.color, { r: 0.0, g: 0.8, b: 1.0, duration: 1.8 });
            for(let i=0; i<particleCount; i++) {
                velocities[i].y = 0.2 + Math.random() * 0.2; 
                velocities[i].x = -0.5 - Math.random() * 0.5;
            }
        } else {
            // Revert back
            gsap.to(".lamp-container", { x: 0, scale: 1, duration: 1.8, ease: "power4.inOut" });
            gsap.to(".light-beam", { clipPath: "polygon(40% 0, 60% 0, 100% 100%, 0% 100%)", filter: "blur(10px)", duration: 1.8, ease: "power4.inOut" });
            gsap.to(".floor-glow", { width: 800, opacity: 0.25, duration: 1.8, ease: "power4.inOut" });
            gsap.to(".login-wrapper", { x: 0, duration: 1.8, ease: "power4.inOut" });
            
            // Background 3D Animation: Shift back to Warm Gold & Swirl Particles Right/Down
            gsap.to(material.color, { r: 0.98, g: 0.8, b: 0.08, duration: 1.8 }); 
            gsap.to(matGeo.color, { r: 0.98, g: 0.8, b: 0.08, duration: 1.8 });
            for(let i=0; i<particleCount; i++) {
                velocities[i].y = -0.2 - Math.random() * 0.2; 
                velocities[i].x = 0.5 + Math.random() * 0.5;
            }
        }
    });
});
