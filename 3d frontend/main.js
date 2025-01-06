import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { FBXLoader } from "three/addons/loaders/FBXLoader.js"; // Use FBXLoader instead of OBJLoader
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// const gltfloader = new GLTFLoader();
const loader = new FBXLoader(); // Use FBXLoader to load FBX models


const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);
const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);

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
        object.position.set(0, 0, 0); // Adjust position if needed
        object.scale.set(0.05, 0.05, 0.05);
        object.position.set(10,1,1)
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
const cameraTexture = textureLoader.load("./esp32camBake.PNG");
loader.load(
  "./camera.fbx", // Path to your FBX file
  (object) => {
      object.traverse((child) => {
          if (child.isMesh) {
              child.material = new THREE.MeshBasicMaterial({ map: cameraTexture }); // Apply texture
          }
      });
      object.position.set(-5, 0, 0); // Adjust position if needed
      object.scale.set(0.05, 0.05, 0.05);
      scene.add(object);



  },
  (xhr) => {
      console.log(`Loading: ${(xhr.loaded / xhr.total) * 100}% complete`);
  },
  (error) => {
      console.error("An error occurred while loading the FBX file:", error);
  }
);
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
cube.position.set(0,0,0)
scene.add(cube);




 
camera.position.z = 5;
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
    try {
    } catch {}
}

renderer.setAnimationLoop(animate);
