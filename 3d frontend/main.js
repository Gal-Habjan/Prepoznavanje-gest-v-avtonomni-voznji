import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

import { FBXLoader } from "three/addons/loaders/FBXLoader.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);
const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);

const renderer = new THREE.WebGLRenderer();
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0x404040, 2); // ambient luc
scene.add(ambientLight);



const directionalLight = new THREE.DirectionalLight(0xffffff, 1); // bela direction
var cube2 = new THREE.Mesh(
    new THREE.BoxGeometry(1, 1, 1),
    new THREE.MeshLambertMaterial({ color: 0xffaaaa })
);

cube2.position.set(10,10,10)
directionalLight.position.set(10,10,10);
directionalLight.castShadow = true;
directionalLight.shadow.camera.near = 0.1;
directionalLight.shadow.camera.far = 1000;
directionalLight.shadow.mapSize.width = 512;
directionalLight.shadow.mapSize.height = 512;
scene.add(directionalLight);
scene.add(cube2);








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

const geometry = new THREE.SphereGeometry(500, 32, 32);
const material = new THREE.ShaderMaterial({
    vertexShader: vertexShader,
    fragmentShader: fragmentShader,
    side: THREE.BackSide
});

const controls = new OrbitControls(camera, renderer.domElement);
const loader_gltf = new GLTFLoader();
const loader = new FBXLoader();
const textureLoader = new THREE.TextureLoader();
const texture = textureLoader.load("./bake-2.png");
let mixer;
let animations = [];
loader.load(
    "./hand.fbx",
    (object) => {
        object.traverse((child) => {
            if (child.isMesh) {
                child.material = new THREE.MeshBasicMaterial({ map: texture });
                child.receiveShadow = true;
                child.castShadow = true;
            }
        });
        object.position.set(0, -10, 20);
        object.scale.set(0.03, 0.03, 0.03);
        object.rotation.y = 90;
        scene.add(object);
        mixer = new THREE.AnimationMixer(object);

        console.log(object.animations);
        object.animations.forEach((clip) => {
            animations.push(clip);
            if (clip.name === "Armature|activeState") {
                const action = mixer.clipAction(clip);
                action.setLoop(THREE.LoopOnce, 1);
                action.clampWhenFinished = true;
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
    "./ReworkedAiCam3.fbx", // Path to your FBX file
    (object) => {
        object.traverse((child) => {
            if (child.isMesh) {
                child.material = new THREE.MeshBasicMaterial({ map: cameraTexture }); // Apply texture
                child.receiveShadow = true;
                child.castShadow = true;
            }
        });
        object.position.set(3, -4.5, 2); // Adjust position if needed
        object.scale.set(0.01, 0.01, 0.01);
        object.rotation.set(Math.PI / 2, 0, 0);
        scene.add(object);



    },
    (xhr) => {

    },
    (error) => {
        console.error("An error occurred while loading the FBX file:", error);
    }
);





camera.position.z = 5;


const sky = new THREE.Mesh(geometry, material);
scene.add(sky);


loader_gltf.load(
    './vent.glb',
    (gltf) => {
        const car = gltf.scene;
        scene.add(car);

        car.traverse((child) => {
            if (child.isMesh) {
                child.receiveShadow = true;
                child.castShadow = true;
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
    './car.glb',
    (gltf) => {
        const car = gltf.scene;
        scene.add(car);

        car.traverse((child) => {
            if (child.isMesh) {
                child.receiveShadow = true;
                child.castShadow = true;
                if (child.name.toLowerCase().includes('vent')) {
                    child.material = new THREE.MeshStandardMaterial({ color: 0xff0000 }); // Red color
                }
            }
        });

        car.position.set(5, -60, 10);
        car.scale.set(40, 40, 40);
        car.rotation.y = 30;
    },
    (xhr) => {
        console.log(`Loading: ${(xhr.loaded / xhr.total) * 100}% complete`);
    },
    (error) => {
        console.error('An error occurred while loading the GLTF file:', error);
    }
);


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
        mixer.update(0.01);
    }
    renderer.render(scene, camera);
    updateAnimationName();
    try {
    } catch { }
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
