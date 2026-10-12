document.addEventListener('DOMContentLoaded', () => {
    // 1. Initial UI Setup
    const appContainer = document.querySelector('.app-container');
    const introContainer = document.getElementById('intro-container');
    
    // Hide main app initially
    gsap.set(appContainer, { opacity: 0, scale: 0.95, filter: "blur(10px)" });

    // 2. Three.js Setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    document.getElementById('webgl-intro').appendChild(renderer.domElement);

    // 3. Create the "AI Core" (Wireframe Object)
    // We use a complex Icosahedron to represent the core
    const coreGeometry = new THREE.IcosahedronGeometry(1.5, 1);
    
    // Create multiple wireframe layers for a high-tech look
    const coreMaterial = new THREE.MeshBasicMaterial({
        color: 0x10b981, // Primary green/cyan
        wireframe: true,
        transparent: true,
        opacity: 0.8
    });
    
    const coreMaterialInner = new THREE.MeshBasicMaterial({
        color: 0x3b82f6, // Secondary blue
        wireframe: true,
        transparent: true,
        opacity: 0.4
    });

    const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
    const innerMesh = new THREE.Mesh(new THREE.IcosahedronGeometry(1.2, 0), coreMaterialInner);
    
    const coreGroup = new THREE.Group();
    coreGroup.add(coreMesh);
    coreGroup.add(innerMesh);
    scene.add(coreGroup);

    // Initial position: hidden at the bottom
    coreGroup.position.set(0, -10, -2);
    camera.position.z = 5;

    // 4. Animation Loop
    let isAnimating = true;
    function animate() {
        if (!isAnimating) return;
        requestAnimationFrame(animate);
        
        // Spin the core
        coreGroup.rotation.y += 0.01;
        coreGroup.rotation.x += 0.005;
        
        innerMesh.rotation.y -= 0.015;
        innerMesh.rotation.z += 0.01;
        
        renderer.render(scene, camera);
    }
    animate();

    // 5. The Cinematic Intro Timeline
    const introTl = gsap.timeline({
        onComplete: () => {
            isAnimating = false;
            introContainer.style.display = 'none';
        }
    });

    // Step A: Pop up from bottom
    introTl.to(coreGroup.position, {
        y: 0,
        duration: 1.5,
        ease: "back.out(1.2)"
    })
    
    // Step B: "Open Up" / Expand
    .to(coreGroup.scale, {
        x: 2.5, y: 2.5, z: 2.5,
        duration: 1.2,
        ease: "power2.inOut"
    })
    .to(coreMaterial, { opacity: 0.2, duration: 1.2 }, "<") // Fade core slightly to see through it
    
    // Step C: Reveal Dashboard UI (Page 1 appears)
    .to(introContainer, { backgroundColor: "rgba(0,0,0,0)", duration: 1 }, "-=0.5")
    .to(appContainer, {
        opacity: 1,
        scale: 1,
        filter: "blur(0px)",
        duration: 1.5,
        ease: "power3.out"
    }, "<")

    // Step D: Slide towards the right and exit
    .to(coreGroup.position, {
        x: 15, // fly far right
        y: 2,
        duration: 1.5,
        ease: "power3.in"
    }, "-=0.5")
    .to(coreGroup.scale, {
        x: 0.1, y: 0.1, z: 0.1,
        duration: 1.5,
        ease: "power3.in"
    }, "<");

    // Handle Resize
    window.addEventListener('resize', () => {
        if(!isAnimating) return;
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
});
