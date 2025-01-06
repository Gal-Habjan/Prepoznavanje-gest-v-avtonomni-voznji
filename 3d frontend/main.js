import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { FBXLoader } from "three/addons/loaders/FBXLoader.js"; // Use FBXLoader instead of OBJLoader
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js"; // Use GLTFLoader


const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0x404040, 2); // ambient luc
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1); // bela direction
directionalLight.position.set(5, 5, 5); 
scene.add(directionalLight);

const vertexShader = `
    varying vec3 vWorldPosition;
    void main() {
        vec4 worldPosition = modelMatrix * vec4(position, 1.0);
        vWorldPosition = worldPosition.xyz;
        gl_Position = projectionMatrix * viewMatrix * worldPosition;
    }
`;

const fragmentShader = `
    varying vec3 vWorldPosition;
    void main() {
        vec3 topColor = vec3(0.4, 0.7, 1.0); // Sky blue color
        vec3 bottomColor = vec3(0.15, 0.15, 0.15); // White color
        float gradient = (vWorldPosition.y + 250.0) / 200.0; // y position
        vec3 color = mix(bottomColor, topColor, gradient);
        gl_FragColor = vec4(color, 1.0);
    }
`;

const geometry = new THREE.SphereGeometry(500, 32, 32); // Sphere to simulate sky
const material = new THREE.ShaderMaterial({
    vertexShader: vertexShader,
    fragmentShader: fragmentShader,
    side: THREE.BackSide 
});

const controls = new OrbitControls(camera, renderer.domElement);
const loader = new FBXLoader(); // Use FBXLoader to load FBX models
const loader_gltf = new GLTFLoader();
const textureLoader = new THREE.TextureLoader();
const texture = textureLoader.load("./bake-2.png"); // Replace with your texture path
let mixer;
let animations = [];
loader.load(
    "./hand.fbx", // Path to your FBX file
    (object) => {
        object.traverse((child) => {
            if (child.isMesh) {
                child.material = new THREE.MeshBasicMaterial({ map: texture }); // Apply texture
            }
        });
        object.position.set(0, -10, 20); // Adjust position if needed
        object.scale.set(0.03, 0.03, 0.03);
        object.rotation.y = 90;
        scene.add(object);
        mixer = new THREE.AnimationMixer(object);

        // Store animations and set up the activeState animation
        console.log(object.animations);
        object.animations.forEach((clip) => {
            animations.push(clip);
            if (clip.name === "Armature|activeState") {
                // Set the animation for "activeState" if it exists
                const action = mixer.clipAction(clip);
                action.setLoop(THREE.LoopOnce, 1); // Play once
                action.clampWhenFinished = true; // Stay at the last frame
                action.play();
            }
        });
    },
    (xhr) => {
        console.log(`Loading: ${(xhr.loaded / xhr.total) * 100}% complete`);
    },
    (error) => {
        console.error("An error occurred while loading the FBX file:", error);
    }
);



const sky = new THREE.Mesh(geometry, material);
scene.add(sky);


loader_gltf.load(
    './vent.glb', // Path to your GLB file
    (gltf) => {
      const car = gltf.scene;
      scene.add(car);
  
      car.traverse((child) => {
        if (child.isMesh) {
          if (child.name.toLowerCase().includes('vent')) {
            child.material = new THREE.MeshStandardMaterial({ color: 0xff0000 }); // Red color
        }
        }
      });
  
      car.position.set(7, -5, 1);
      car.scale.set(2.7, 2.7, 2.7);
      car.rotation.y = 0.15;
    },
    (xhr) => {
      console.log(`Loading: ${(xhr.loaded / xhr.total) * 100}% complete`);
    },
    (error) => {
      console.error('An error occurred while loading the GLTF file:', error);
    }
  );

  loader_gltf.load(
    './car.glb', // Path to your GLB file
    (gltf) => {
      const car = gltf.scene;
      scene.add(car);
  
      car.traverse((child) => {
        if (child.isMesh) {
          if (child.name.toLowerCase().includes('vent')) {
            child.material = new THREE.MeshStandardMaterial({ color: 0xff0000 }); // Red color
        }
        }
      });
  
      car.position.set(5, -60, 10);
      car.scale.set(40,40,40);
      car.rotation.y = 30;
    },
    (xhr) => {
      console.log(`Loading: ${(xhr.loaded / xhr.total) * 100}% complete`);
    },
    (error) => {
      console.error('An error occurred while loading the GLTF file:', error);
    }
  );

  //scene.background = new THREE.Color(0x87CEEB); // Light blue color

/*
  const geometry = new THREE.BoxGeometry(5,5,5);
  const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
  const cube = new THREE.Mesh(geometry, material);
  cube.position.set(5,5,-15);
  scene.add(cube);*/

camera.position.z = 30;
const socket = new WebSocket("ws://localhost:8765");

socket.onopen = () => {
    console.log("Connected to WebSocket!");
    socket.send("Hello Server!");
};

socket.onmessage = (event) => {
    console.log("Received:", event.data);
};

socket.onerror = (error) => {
    console.error("WebSocket Error:", error);
};

socket.onclose = (event) => {
    console.log("WebSocket Closed.", event);
};

function animate() {
    if (mixer) {
        mixer.update(0.01); // Update the mixer with deltaTime
    }
    renderer.render(scene, camera);
    updateAnimationName();
    try {
    } catch {}
}

const animationNameElement = document.getElementById('animationName');

let currentAnimationName = '';

function updateAnimationName() {
    if (mixer && mixer._actions.length > 0) {
        const currentAction = mixer._actions[0];
        if (currentAction && currentAction.getClip()) {
            const animationName = currentAction.getClip().name;
            // update text ce je druga animacija
            if (currentAnimationName !== animationName) {
                currentAnimationName = animationName;
                animationNameElement.textContent = `Animation: ${currentAnimationName}`;
            }
        }
    }
}


//demo animacije
document.getElementById('animateButton').addEventListener('click', () => {
    if (mixer) {
        const action = mixer.clipAction(animations[0]); 
        action.reset().play();
        
    }
});


renderer.setAnimationLoop(animate);
