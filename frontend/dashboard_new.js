document.addEventListener('DOMContentLoaded', () => {
    const introContainer = document.getElementById('intro-container');
    const webglContainer = document.getElementById('webgl-container');
    const introFlash = document.getElementById('intro-flash');
    const appWrapper = document.getElementById('app-wrapper');

    // 1. Three.js Setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    webglContainer.appendChild(renderer.domElement);

    // Group to hold the orb
    const orbGroup = new THREE.Group();
    scene.add(orbGroup);

    // 2. Create the 3D Interactive Circular Element (Orb)
    const orbGeometry = new THREE.IcosahedronGeometry(2, 2); // highly detailed sphere
    const orbMaterial = new THREE.MeshBasicMaterial({
        color: 0xc96dff, // glowing purple/pink
        wireframe: true,
        transparent: true,
        opacity: 0.8
    });
    const innerOrbMaterial = new THREE.MeshBasicMaterial({
        color: 0xffd4a3, // warm core
        wireframe: true,
        transparent: true,
        opacity: 0.3
    });

    const orbMesh = new THREE.Mesh(orbGeometry, orbMaterial);
    const innerOrbMesh = new THREE.Mesh(new THREE.IcosahedronGeometry(1.5, 1), innerOrbMaterial);

    orbGroup.add(orbMesh);
    orbGroup.add(innerOrbMesh);

    // Initial position: hidden at the bottom
    orbGroup.position.set(0, -10, -5);
    camera.position.z = 8;

    let isAnimating = true;

    // Pop up animation
    gsap.to(orbGroup.position, {
        y: 0,
        duration: 1.5,
        ease: "back.out(1.2)",
        delay: 0.2
    });

    // 3. Motion Tracking (Attached to window so it always works!)
    let targetRotationX = 0;
    let targetRotationY = 0;

    const heroContent = document.querySelector('.hero-content');
    const optionsGrid = document.querySelector('.options-grid');
    const cursorGlow = document.getElementById('cursor-glow');
    const floatBadges = document.querySelectorAll('.float-badge');

    window.addEventListener('mousemove', (e) => {
        // Normalize mouse coordinates to -1 .. 1
        const mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        const mouseY = -(e.clientY / window.innerHeight) * 2 + 1;

        targetRotationY = mouseX * 0.5;
        targetRotationX = -mouseY * 0.5;

        // Move custom ambient glow cursor
        if (cursorGlow) {
            gsap.to(cursorGlow, {
                x: e.clientX,
                y: e.clientY,
                duration: 1,
                ease: "power2.out"
            });
        }

        // Apply motion tracking (parallax) to the website UI
        if (heroContent && optionsGrid) {
            gsap.to(heroContent, {
                x: mouseX * 20,
                y: -mouseY * 20,
                duration: 1,
                ease: "power2.out"
            });
            gsap.to(optionsGrid, {
                x: mouseX * 10,
                y: -mouseY * 10,
                duration: 1.2,
                ease: "power2.out"
            });
        }
        
        // Deep parallax on floating badges to give them lots of 3D depth
        if (floatBadges.length > 0) {
            floatBadges.forEach((badge, i) => {
                const depth = (i + 1) * 15;
                gsap.to(badge, {
                    x: mouseX * depth,
                    y: -mouseY * depth,
                    duration: 1.5,
                    ease: "power2.out"
                });
            });
        }
    });

    // Animation Loop
    function animate() {
        if (!isAnimating) return;
        requestAnimationFrame(animate);

        // Idle spinning
        orbMesh.rotation.y += 0.005;
        innerOrbMesh.rotation.x -= 0.01;
        innerOrbMesh.rotation.y += 0.01;

        // Motion tracking easing
        orbGroup.rotation.y += (targetRotationY - orbGroup.rotation.y) * 0.1;
        orbGroup.rotation.x += (targetRotationX - orbGroup.rotation.x) * 0.1;

        renderer.render(scene, camera);
    }
    animate();

    // 4. Click interaction
    webglContainer.addEventListener('click', () => {
        webglContainer.style.pointerEvents = 'none';
        document.body.style.cursor = 'default';

        const tl = gsap.timeline();

        // "huge beam of light" & move the ball straight to the right side
        tl.to(introFlash, { opacity: 1, duration: 0.3, ease: "power2.in" })
            .to(orbGroup.scale, { x: 1.5, y: 1.5, z: 1.5, duration: 0.8, ease: "power3.inOut" }, "<") // Scale slightly to look beautiful
            .to(orbGroup.position, { x: 6, y: 0, duration: 0.8, ease: "power3.inOut" }, "<") // Move to RIGHT side and stay there!

            // Reveal the main app wrapper
            .set(appWrapper, { visibility: 'visible' })
            .set(introContainer, { backgroundColor: "transparent", pointerEvents: "none" }) // Remove black bg
            .add(() => {
                // Drop WebGL to background so UI is clickable!
                webglContainer.style.zIndex = '1';
                webglContainer.style.pointerEvents = 'none';

                // We also hide the orange/purple CSS blobs so the 3D orb is the star of the show
                document.querySelector('.blob-purple').style.display = 'none';

                // Enable body scrolling so they can scroll down to the options
                document.body.style.overflow = 'auto';
            })

            // Fade the flash away to reveal the UI and the rotating orb
            .to(introFlash, { opacity: 0, duration: 1, ease: "power2.out" })
            .to(appWrapper, { opacity: 1, duration: 1, ease: "power2.out" }, "<");

        // NOTE: We do NOT stop the animation or hide webglContainer!
    });

    // Remove old scroll logic from here since it's now inside the click handler

    // Add some subtle hover effects for the dashboard UI
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Only prevent default if it's a dummy link
            if (link.getAttribute('href') === '#') {
                e.preventDefault();
            }
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Handle Resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
});


// Tracker Logic
const waterGlasses = document.querySelectorAll('.water-glass');
const waterStatus = document.querySelector('.water-status');
if (waterGlasses && waterStatus) {
    waterGlasses.forEach((glass, index) => {
        glass.addEventListener('click', () => {
            // Fill all glasses up to the clicked one
            waterGlasses.forEach((g, i) => {
                if (i <= index) {
                    g.classList.add('filled');
                } else {
                    g.classList.remove('filled');
                }
            });
            waterStatus.innerText = `${index + 1} / 8 Glasses (${(index + 1) * 250}ml)`;
            
            // Tiny GSAP bounce
            gsap.fromTo(glass, { scale: 0.8 }, { scale: 1.1, duration: 0.3, ease: 'back.out(2)' });
        });
    });
}

const mealItems = document.querySelectorAll('.meal-check-item');
if (mealItems) {
    mealItems.forEach(item => {
        item.addEventListener('click', () => {
            const icon = item.querySelector('i');
            if (item.classList.contains('completed')) {
                item.classList.remove('completed');
                icon.className = 'fa-regular fa-circle';
            } else {
                item.classList.add('completed');
                icon.className = 'fa-solid fa-circle-check';
                gsap.fromTo(icon, { scale: 0.5 }, { scale: 1, duration: 0.4, ease: 'back.out(2)' });
            }
        });
    });
}

// Camera and Mic Functionality
const cameraBtnDashboard = document.getElementById('camera-btn-dashboard');
if (cameraBtnDashboard) {
    cameraBtnDashboard.addEventListener('click', () => {
        window.location.href = 'scanner.html';
    });
}

const micBtnDashboard = document.getElementById('mic-btn-dashboard');
const promptInput = document.querySelector('input[name="q"]');

if (micBtnDashboard && promptInput) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        let isRecording = false;
        let pulseTween;

        micBtnDashboard.addEventListener('click', () => {
            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });

        recognition.onstart = () => {
            isRecording = true;
            promptInput.placeholder = "Listening...";
            micBtnDashboard.style.color = '#ff5e5e';
            pulseTween = gsap.to(micBtnDashboard, { scale: 1.2, duration: 0.5, yoyo: true, repeat: -1 });
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            promptInput.value = transcript;
        };

        recognition.onend = () => {
            isRecording = false;
            micBtnDashboard.style.color = '';
            if (pulseTween) pulseTween.kill();
            gsap.to(micBtnDashboard, { scale: 1, duration: 0.2 });
            promptInput.placeholder = "Ask Healthy Food...";
            
            if(promptInput.value.trim().length > 0) {
                promptInput.closest('form').submit();
            }
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            isRecording = false;
            micBtnDashboard.style.color = '';
            if (pulseTween) pulseTween.kill();
            gsap.to(micBtnDashboard, { scale: 1, duration: 0.2 });
            promptInput.placeholder = "Ask Healthy Food...";
        };
    } else {
        micBtnDashboard.addEventListener('click', () => {
            alert("Speech Recognition API is not supported in this browser.");
        });
    }
}
