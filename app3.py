# ==============================================================================
# CELL 1: GENERATE GAME FILES AND LAUNCH SERVER
# ==============================================================================

import os
import threading
import http.server
import socketserver
from google.colab import output

# 1. Create project directory
GAME_DIR = '/content/hospital_game'
os.makedirs(GAME_DIR, exist_ok=True)

# 2. Generate HTML
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Abandoned Wing - 3D Puzzle</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- 3D Canvas -->
    <div id="game-container"></div>
    
    <!-- Crosshair -->
    <div id="crosshair"></div>
    
    <!-- Main Menu -->
    <div id="main-menu" class="ui-layer">
        <h1>THE ABANDONED WING</h1>
        <p>A First-Person Investigation</p>
        <button id="btn-start">ENTER HOSPITAL</button>
        <p class="instructions">WASD to Move | MOUSE to Look | E to Interact</p>
    </div>
    
    <!-- HUD -->
    <div id="hud" class="ui-layer hidden">
        <div id="level-display">Level 1: Reception</div>
        <div id="evidence-counter">Evidence: 0/0</div>
        <div id="interaction-prompt" class="hidden">Press E to Inspect</div>
    </div>
    
    <!-- Inspection Panel -->
    <div id="inspection-panel" class="ui-layer hidden">
        <h2 id="inspect-title">Document</h2>
        <div id="inspect-content">...</div>
        <button id="btn-close-inspect">Close (E)</button>
    </div>
    
    <!-- Scroll/Clue Panel -->
    <div id="scroll-panel" class="ui-layer hidden">
        <h2>Cryptic Note</h2>
        <p id="scroll-content">...</p>
        <div class="hint-section">
            <button id="btn-hint">Need a Hint?</button>
            <p id="hint-text" class="hidden"></p>
        </div>
        <button id="btn-close-scroll">Close (E)</button>
    </div>
    
    <!-- Keypad -->
    <div id="keypad-panel" class="ui-layer hidden">
        <div id="keypad-display">----</div>
        <div class="keypad-grid">
            <button class="kp-btn">1</button><button class="kp-btn">2</button><button class="kp-btn">3</button>
            <button class="kp-btn">4</button><button class="kp-btn">5</button><button class="kp-btn">6</button>
            <button class="kp-btn">7</button><button class="kp-btn">8</button><button class="kp-btn">9</button>
            <button class="kp-btn kp-clear">CLR</button><button class="kp-btn">0</button><button class="kp-btn kp-enter">ENT</button>
        </div>
        <button id="btn-close-keypad">Step Away (E)</button>
    </div>
    
    <!-- End Screen -->
    <div id="end-screen" class="ui-layer hidden">
        <h1>MYSTERY SOLVED</h1>
        <p>You have successfully navigated the abandoned wing.</p>
        <button id="btn-restart">PLAY AGAIN</button>
    </div>

    <!-- Three.js (via CDN) -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>
    
    <!-- Game Logic -->
    <script src="game.js"></script>
</body>
</html>
"""

# 3. Generate CSS
css_content = """
* { margin: 0; padding: 0; box-sizing: border-box; user-select: none; font-family: 'Courier New', Courier, monospace; }
body { background: #000; overflow: hidden; color: #fff; }
#game-container { position: absolute; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1; }
.ui-layer { position: absolute; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.8); backdrop-filter: blur(3px); }
.hidden { display: none !important; }
#crosshair { position: absolute; top: 50%; left: 50%; width: 4px; height: 4px; background: rgba(255,255,255,0.7); border-radius: 50%; transform: translate(-50%, -50%); z-index: 5; pointer-events: none; }

h1 { font-size: 3rem; margin-bottom: 10px; color: #a3c2c2; text-shadow: 0 0 10px #a3c2c2; letter-spacing: 2px; text-align: center; }
h2 { font-size: 2rem; margin-bottom: 20px; color: #e0e0e0; border-bottom: 1px solid #555; padding-bottom: 10px; }
p { font-size: 1.2rem; margin-bottom: 30px; text-align: center; max-width: 600px; line-height: 1.5; color: #ccc; }

button { padding: 15px 30px; font-size: 1.2rem; background: #222; color: #fff; border: 1px solid #555; cursor: pointer; transition: all 0.2s; text-transform: uppercase; letter-spacing: 1px; }
button:hover { background: #444; border-color: #a3c2c2; box-shadow: 0 0 15px rgba(163, 194, 194, 0.5); }

#hud { background: transparent; justify-content: space-between; align-items: flex-start; padding: 20px; pointer-events: none; }
#level-display, #evidence-counter { font-size: 1.5rem; text-shadow: 1px 1px 2px #000; background: rgba(0,0,0,0.5); padding: 5px 15px; border: 1px solid #333; }
#evidence-counter { position: absolute; top: 20px; right: 20px; }
#interaction-prompt { position: absolute; bottom: 20%; left: 50%; transform: translateX(-50%); font-size: 1.5rem; background: rgba(0,0,0,0.7); padding: 10px 20px; border: 1px solid #fff; }

#inspection-panel, #scroll-panel { background: rgba(10, 15, 20, 0.95); }
#inspect-content, #scroll-content { background: #fff; color: #111; padding: 30px; border-radius: 2px; width: 80%; max-width: 500px; min-height: 300px; font-family: 'Times New Roman', serif; box-shadow: inset 0 0 50px rgba(0,0,0,0.1); }
#scroll-content { background: #f4e8c1; color: #3d2b1f; font-style: italic; border: 2px solid #a8946e; }

.hint-section { margin-top: 20px; text-align: center; }
#hint-text { color: #a3c2c2; font-size: 1rem; margin-top: 10px; }

#keypad-panel { background: rgba(0,0,0,0.85); }
#keypad-display { font-size: 3rem; background: #111; color: #0f0; border: 2px solid #333; padding: 10px 20px; margin-bottom: 20px; width: 320px; text-align: center; font-family: monospace; text-shadow: 0 0 10px #0f0; }
.keypad-grid { display: grid; grid-template-columns: repeat(3, 100px); gap: 10px; margin-bottom: 30px; }
.kp-btn { height: 80px; font-size: 2rem; background: #333; border-radius: 5px; box-shadow: inset 0 0 10px rgba(0,0,0,0.8); }
.kp-btn:hover { background: #555; }
.kp-clear { background: #522; color: #f55; }
.kp-enter { background: #252; color: #5f5; }
"""

# 4. Generate JavaScript (Engine, Procedural Gen, Puzzles)
js_content = """
// --- AUDIO SYSTEM (Procedural Web Audio API) ---
class AudioManager {
    constructor() {
        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        this.ambientOsc = null;
        this.ambientGain = null;
    }
    
    startAmbient() {
        if(this.ambientOsc) return;
        this.ambientOsc = this.ctx.createOscillator();
        this.ambientGain = this.ctx.createGain();
        this.ambientOsc.type = 'sine';
        this.ambientOsc.frequency.setValueAtTime(55, this.ctx.currentTime); // Low hum
        this.ambientGain.gain.setValueAtTime(0.1, this.ctx.currentTime);
        this.ambientOsc.connect(this.ambientGain);
        this.ambientGain.connect(this.ctx.destination);
        this.ambientOsc.start();
    }
    
    playBeep(freq, type, duration, vol=0.1) {
        if(this.ctx.state === 'suspended') this.ctx.resume();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        gain.gain.setValueAtTime(vol, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + duration);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + duration);
    }

    playFootstep() {
        this.playBeep(Math.random() * 50 + 100, 'square', 0.1, 0.02);
    }
    
    playDoorUnlock() {
        this.playBeep(880, 'sine', 0.1, 0.2);
        setTimeout(() => this.playBeep(1760, 'sine', 0.3, 0.2), 150);
    }
    
    playError() {
        this.playBeep(150, 'sawtooth', 0.4, 0.3);
    }
}

// --- GAME DATA & PUZZLES ---
const LEVELS = [
    {
        name: "Level 1: Reception",
        color: 0xe0e0e0, ambient: 0x404040,
        layout: { w: 30, d: 30 },
        code: "0899",
        clue: "Only the Morning Shift and the Emergency Code matter. Combine them.",
        hints: ["Look at the Shift Logs and the Emergency Memo.", "Morning shift is 0800. Emergency is 99.", "The code is 08 followed by 99."],
        evidence: [
            { type: 'doc', title: "Shift Log A", content: "Morning Shift Start: 0800 hrs. Status: Normal.", pos: [5, 1.5, -5], found: false },
            { type: 'doc', title: "Shift Log B", content: "Evening Shift Start: 1600 hrs. Status: Quiet.", pos: [-5, 1.5, 5], found: false },
            { type: 'doc', title: "Emergency Memo", content: "Reminder: In case of absolute lockdown, broadcast Code 99.", pos: [2, 1.5, 10], found: false }
        ]
    },
    {
        name: "Level 2: Patient Room 20",
        color: 0xccd9ff, ambient: 0x203040,
        layout: { w: 25, d: 35 },
        code: "9950",
        clue: "The patient's birth year divided by their room number. Then append the medication dosage.",
        hints: ["Find the patient's bracelet for their birth year.", "The room number is in the level title (20).", "1980 / 20 = 99. Dosage is 50. Code: 9950."],
        evidence: [
            { type: 'doc', title: "Patient ID Bracelet", content: "Name: John Doe\\nDOB: 1980\\nAdmitted: Yesterday", pos: [-8, 1, -2], found: false },
            { type: 'doc', title: "Medication Chart", content: "Administer 50mg of Sedative every 4 hours.", pos: [8, 1.5, -10], found: false },
            { type: 'doc', title: "Dietary Note", content: "Patient is allergic to peanuts. Room 20 meal adjusted.", pos: [0, 1.5, 12], found: false }
        ]
    },
    {
        name: "Level 3: Nurse Station",
        color: 0xd9ead3, ambient: 0x304030,
        layout: { w: 40, d: 30 },
        code: "1479",
        clue: "Order the incident reports chronologically by date. Enter the incident codes in that order.",
        hints: ["Find the 4 incident reports scattered around.", "Order them from Jan 1st to Jan 5th.", "Jan 1 (Code 1), Jan 2 (Code 4), Jan 3 (Code 7), Jan 5 (Code 9)."],
        evidence: [
            { type: 'doc', title: "Incident Report", content: "Date: Jan 3\\nEvent: Code Blue\\nLog Code: 7", pos: [-10, 1.5, -5], found: false },
            { type: 'doc', title: "Incident Report", content: "Date: Jan 1\\nEvent: Missing Keys\\nLog Code: 1", pos: [15, 1.5, 8], found: false },
            { type: 'doc', title: "Incident Report", content: "Date: Jan 2\\nEvent: Power Outage\\nLog Code: 4", pos: [5, 1.5, -12], found: false },
            { type: 'doc', title: "Incident Report", content: "Date: Jan 5\\nEvent: Unauthorized Access\\nLog Code: 9", pos: [-15, 1.5, 10], found: false }
        ]
    },
    {
        name: "Level 4: Medical Records",
        color: 0xead1dc, ambient: 0x402020,
        layout: { w: 35, d: 35 },
        code: "8135",
        clue: "Blue, Green, Red, Yellow. Alphabetical order of the colors.",
        hints: ["There are four colored folders.", "Alphabetical: Blue, Green, Red, Yellow.", "Look at the numbers inside those specific folders. 8-1-3-5."],
        evidence: [
            { type: 'doc', title: "Red Folder", content: "Archive Sector: 3", pos: [12, 1.5, -12], found: false },
            { type: 'doc', title: "Blue Folder", content: "Archive Sector: 8", pos: [-12, 1.5, 12], found: false },
            { type: 'doc', title: "Green Folder", content: "Archive Sector: 1", pos: [12, 1.5, 12], found: false },
            { type: 'doc', title: "Yellow Folder", content: "Archive Sector: 5", pos: [-12, 1.5, -12], found: false },
            { type: 'doc', title: "Black Folder", content: "Archive Sector: 9 (Discarded)", pos: [0, 1.5, 0], found: false }
        ]
    },
    {
        name: "Level 5: Laboratory",
        color: 0xffffff, ambient: 0x505050,
        layout: { w: 30, d: 40 },
        code: "1800",
        clue: "Take the boiling point of the volatile chemical, subtract the freezing point of the stable chemical, and add a zero at the end.",
        hints: ["Find the chemical data sheets.", "Boiling pt is 212. Freezing pt is 32.", "212 - 32 = 180. Add 0 -> 1800."],
        evidence: [
            { type: 'doc', title: "Chemical X Data", content: "Type: Stable\\nFreezing Point: 32 F\\nSafe for transport.", pos: [8, 1.5, -15], found: false },
            { type: 'doc', title: "Chemical Y Data", content: "Type: Volatile\\nBoiling Point: 212 F\\nRequires containment.", pos: [-8, 1.5, 15], found: false },
            { type: 'doc', title: "Lab Technician Note", content: "Remember to calibrate the scale to 100 before mixing.", pos: [10, 1.5, 5], found: false }
        ]
    },
    {
        name: "Level 6: Operating Room",
        color: 0xc9daf8, ambient: 0x203040,
        layout: { w: 40, d: 40 },
        code: "0075",
        clue: "Sum the total number of surgical instruments logged. Reverse the number, and pad with zeroes to make it 4 digits.",
        hints: ["Add the quantities of Scalpels, Forceps, and Sutures.", "15 + 32 + 10 = 57.", "Reverse 57 to get 75. Pad to 4 digits: 0075."],
        evidence: [
            { type: 'doc', title: "Inventory Log A", content: "Scalpels used: 15\\nCondition: Sterilized", pos: [-15, 1.5, -5], found: false },
            { type: 'doc', title: "Inventory Log B", content: "Forceps used: 32\\nCondition: Requires cleaning", pos: [15, 1.5, -10], found: false },
            { type: 'doc', title: "Inventory Log C", content: "Sutures used: 10\\nCondition: Depleted", pos: [0, 1.5, 15], found: false },
            { type: 'doc', title: "Nurse's Note", content: "The patient's heart rate dropped to 40 BPM.", pos: [-5, 1.5, 5], found: false }
        ]
    },
    {
        name: "Level 7: Restricted Archive",
        color: 0x333333, ambient: 0x101010,
        layout: { w: 50, d: 50 },
        code: "9454",
        clue: "Digit 1: Highest single digit.\\nDigit 2: Square root of 16.\\nDigit 3: Digit 2 plus 1.\\nDigit 4: Digit 1 minus Digit 3.",
        hints: ["Follow the math step by step.", "Digit 1 is 9. Digit 2 is 4.", "Digit 3 is 5. Digit 4 is (9 - 5) = 4. Code: 9454."],
        evidence: [
            { type: 'doc', title: "Fragment 1", content: "The founder always liked prime numbers, but the first digit is the absolute highest single digit.", pos: [-20, 1.5, -20], found: false },
            { type: 'doc', title: "Fragment 2", content: "The second digit is the square root of the number of beds in the old ward (16).", pos: [20, 1.5, 20], found: false },
            { type: 'doc', title: "Fragment 3", content: "The third is simply the second digit plus one.", pos: [-20, 1.5, 20], found: false },
            { type: 'doc', title: "Fragment 4", content: "The final digit is the first minus the third.", pos: [20, 1.5, -20], found: false }
        ]
    }
];

// --- 3D ENGINE & GAME STATE ---
class Game {
    constructor() {
        this.audio = new AudioManager();
        this.levelIndex = 0;
        this.state = 'menu'; // menu, playing, inspecting, keypad, end
        this.evidenceFound = 0;
        this.hintsUsed = 0;
        
        this.setupThreeJS();
        this.setupUI();
        this.animate();
    }
    
    setupThreeJS() {
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.FogExp2(0x000000, 0.02);
        
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: false });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.getElementById('game-container').appendChild(this.renderer.domElement);
        
        this.controls = new THREE.PointerLockControls(this.camera, document.body);
        
        this.raycaster = new THREE.Raycaster();
        this.center = new THREE.Vector2(0, 0);
        
        this.interactables = [];
        this.move = { f: false, b: false, l: false, r: false };
        this.velocity = new THREE.Vector3();
        this.direction = new THREE.Vector3();
        this.prevTime = performance.now();
        
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });
        
        document.addEventListener('keydown', (e) => this.onKeyDown(e));
        document.addEventListener('keyup', (e) => this.onKeyUp(e));
    }
    
    setupUI() {
        document.getElementById('btn-start').addEventListener('click', () => {
            this.audio.ctx.resume();
            this.audio.startAmbient();
            document.getElementById('main-menu').classList.add('hidden');
            this.loadLevel(this.levelIndex);
        });
        
        document.getElementById('btn-close-inspect').addEventListener('click', () => this.resumeGame());
        document.getElementById('btn-close-scroll').addEventListener('click', () => this.resumeGame());
        document.getElementById('btn-close-keypad').addEventListener('click', () => this.resumeGame());
        document.getElementById('btn-restart').addEventListener('click', () => {
            document.getElementById('end-screen').classList.add('hidden');
            this.levelIndex = 0;
            this.loadLevel(0);
        });
        
        document.getElementById('btn-hint').addEventListener('click', () => {
            const hints = LEVELS[this.levelIndex].hints;
            if(this.hintsUsed < hints.length) {
                document.getElementById('hint-text').innerText = hints[this.hintsUsed];
                document.getElementById('hint-text').classList.remove('hidden');
                this.hintsUsed++;
            }
        });
        
        // Keypad logic
        this.enteredCode = "";
        document.querySelectorAll('.kp-btn:not(.kp-clear):not(.kp-enter)').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if(this.enteredCode.length < 4) {
                    this.enteredCode += e.target.innerText;
                    this.updateKeypadDisplay();
                    this.audio.playBeep(600, 'sine', 0.1);
                }
            });
        });
        document.querySelector('.kp-clear').addEventListener('click', () => {
            this.enteredCode = "";
            this.updateKeypadDisplay();
            this.audio.playBeep(400, 'square', 0.1);
        });
        document.querySelector('.kp-enter').addEventListener('click', () => {
            const correct = LEVELS[this.levelIndex].code;
            if(this.enteredCode === correct) {
                this.audio.playDoorUnlock();
                document.getElementById('keypad-display').style.color = '#0f0';
                document.getElementById('keypad-display').innerText = "UNLOCKED";
                setTimeout(() => {
                    this.levelIndex++;
                    if(this.levelIndex >= LEVELS.length) {
                        this.showEndScreen();
                    } else {
                        this.loadLevel(this.levelIndex);
                    }
                }, 1000);
            } else {
                this.audio.playError();
                document.getElementById('keypad-display').style.color = '#f00';
                document.getElementById('keypad-display').innerText = "ERROR";
                setTimeout(() => {
                    this.enteredCode = "";
                    this.updateKeypadDisplay();
                    document.getElementById('keypad-display').style.color = '#0f0';
                }, 1000);
            }
        });
    }
    
    updateKeypadDisplay() {
        let disp = this.enteredCode;
        while(disp.length < 4) disp += "-";
        document.getElementById('keypad-display').innerText = disp;
    }
    
    onKeyDown(event) {
        if (this.state !== 'playing') {
            if (event.code === 'KeyE') {
                if(this.state === 'inspecting' || this.state === 'keypad') this.resumeGame();
            }
            return;
        }
        switch (event.code) {
            case 'KeyW': this.move.f = true; break;
            case 'KeyA': this.move.l = true; break;
            case 'KeyS': this.move.b = true; break;
            case 'KeyD': this.move.r = true; break;
            case 'KeyE': this.interact(); break;
        }
    }
    
    onKeyUp(event) {
        switch (event.code) {
            case 'KeyW': this.move.f = false; break;
            case 'KeyA': this.move.l = false; break;
            case 'KeyS': this.move.b = false; break;
            case 'KeyD': this.move.r = false; break;
        }
    }
    
    resumeGame() {
        document.querySelectorAll('.ui-layer').forEach(el => el.classList.add('hidden'));
        document.getElementById('hud').classList.remove('hidden');
        this.state = 'playing';
        this.controls.lock();
    }
    
    showEndScreen() {
        document.exitPointerLock();
        this.state = 'end';
        document.querySelectorAll('.ui-layer').forEach(el => el.classList.add('hidden'));
        document.getElementById('end-screen').classList.remove('hidden');
    }
    
    loadLevel(index) {
        this.scene.clear();
        this.interactables = [];
        this.evidenceFound = 0;
        this.hintsUsed = 0;
        const level = LEVELS[index];
        
        document.getElementById('level-display').innerText = level.name;
        document.getElementById('evidence-counter').innerText = `Evidence: 0/${level.evidence.length}`;
        document.getElementById('hud').classList.remove('hidden');
        document.getElementById('hint-text').classList.add('hidden');
        document.getElementById('hint-text').innerText = "";
        
        // Ambient Light
        const ambient = new THREE.AmbientLight(level.ambient);
        this.scene.add(ambient);
        
        // Flickering Main Light
        const pointLight = new THREE.PointLight(0xffffee, 1, 50);
        pointLight.position.set(0, 8, 0);
        pointLight.castShadow = true;
        this.scene.add(pointLight);
        this.mainLight = pointLight;
        
        // Procedural Room (Box)
        const roomGeo = new THREE.BoxGeometry(level.layout.w, 10, level.layout.d);
        const roomMat = new THREE.MeshLambertMaterial({ color: level.color, side: THREE.BackSide });
        const room = new THREE.Mesh(roomGeo, roomMat);
        room.receiveShadow = true;
        this.scene.add(room);
        this.roomBounds = { x: level.layout.w/2 - 1, z: level.layout.d/2 - 1 };
        
        // Generate Furniture procedurally
        for(let i=0; i<5; i++) {
            const tableGeo = new THREE.BoxGeometry(4, 1, 2);
            const tableMat = new THREE.MeshLambertMaterial({ color: 0x555555 });
            const table = new THREE.Mesh(tableGeo, tableMat);
            table.position.set(
                (Math.random() - 0.5) * (level.layout.w - 8), 
                1, 
                (Math.random() - 0.5) * (level.layout.d - 8)
            );
            table.castShadow = true;
            table.receiveShadow = true;
            this.scene.add(table);
        }
        
        // Door & Keypad
        const doorGeo = new THREE.BoxGeometry(4, 7, 0.5);
        const doorMat = new THREE.MeshLambertMaterial({ color: 0x331111 });
        const door = new THREE.Mesh(doorGeo, doorMat);
        door.position.set(0, 3.5, -level.layout.d/2 + 0.25);
        this.scene.add(door);
        
        const padGeo = new THREE.BoxGeometry(0.5, 0.8, 0.2);
        const padMat = new THREE.MeshLambertMaterial({ color: 0x111111 });
        const pad = new THREE.Mesh(padGeo, padMat);
        pad.position.set(2.5, 4, -level.layout.d/2 + 0.3);
        pad.userData = { type: 'keypad' };
        this.scene.add(pad);
        this.interactables.push(pad);
        
        // Clue Scroll
        const scrollGeo = new THREE.CylinderGeometry(0.2, 0.2, 1, 8);
        const scrollMat = new THREE.MeshLambertMaterial({ color: 0xddccaa });
        const scroll = new THREE.Mesh(scrollGeo, scrollMat);
        scroll.rotation.z = Math.PI/2;
        scroll.position.set(-2, 1.6, -level.layout.d/2 + 2);
        scroll.userData = { type: 'scroll', clue: level.clue };
        this.scene.add(scroll);
        this.interactables.push(scroll);
        
        // Evidence items
        level.evidence.forEach((ev, i) => {
            const evGeo = new THREE.BoxGeometry(0.6, 0.1, 0.8);
            const evMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
            const evMesh = new THREE.Mesh(evGeo, evMat);
            evMesh.position.set(...ev.pos);
            evMesh.userData = { type: 'evidence', data: ev, index: i };
            
            // Highlight light
            const light = new THREE.PointLight(0x55aaff, 0.5, 3);
            light.position.set(0, 0.5, 0);
            evMesh.add(light);
            
            this.scene.add(evMesh);
            this.interactables.push(evMesh);
        });
        
        this.camera.position.set(0, 4, level.layout.d/2 - 2);
        this.camera.rotation.set(0,0,0);
        this.controls.getObject().position.copy(this.camera.position);
        
        this.resumeGame();
    }
    
    interact() {
        this.raycaster.setFromCamera(this.center, this.camera);
        const intersects = this.raycaster.intersectObjects(this.interactables);
        if (intersects.length > 0 && intersects[0].distance < 6) {
            const obj = intersects[0].object;
            const data = obj.userData;
            
            document.exitPointerLock();
            this.state = 'inspecting';
            this.audio.playBeep(800, 'sine', 0.1);
            
            if (data.type === 'evidence') {
                if(!data.data.found) {
                    data.data.found = true;
                    this.evidenceFound++;
                    document.getElementById('evidence-counter').innerText = `Evidence: ${this.evidenceFound}/${LEVELS[this.levelIndex].evidence.length}`;
                    obj.children[0].intensity = 0; // turn off highlight
                }
                document.getElementById('inspect-title').innerText = data.data.title;
                document.getElementById('inspect-content').innerText = data.data.content;
                document.getElementById('inspection-panel').classList.remove('hidden');
                
            } else if (data.type === 'scroll') {
                document.getElementById('scroll-content').innerText = data.clue;
                document.getElementById('scroll-panel').classList.remove('hidden');
                
            } else if (data.type === 'keypad') {
                this.state = 'keypad';
                this.enteredCode = "";
                this.updateKeypadDisplay();
                document.getElementById('keypad-panel').classList.remove('hidden');
            }
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        const time = performance.now();
        const delta = (time - this.prevTime) / 1000;
        
        if (this.state === 'playing') {
            // Movement physics
            this.velocity.x -= this.velocity.x * 10.0 * delta;
            this.velocity.z -= this.velocity.z * 10.0 * delta;
            
            this.direction.z = Number(this.move.f) - Number(this.move.b);
            this.direction.x = Number(this.move.r) - Number(this.move.l);
            this.direction.normalize();
            
            const speed = 40.0;
            if (this.move.f || this.move.b) this.velocity.z -= this.direction.z * speed * delta;
            if (this.move.l || this.move.r) this.velocity.x -= this.direction.x * speed * delta;
            
            this.controls.moveRight(-this.velocity.x * delta);
            this.controls.moveForward(-this.velocity.z * delta);
            
            // Wall collisions (AABB)
            const pos = this.controls.getObject().position;
            if(pos.x < -this.roomBounds.x) pos.x = -this.roomBounds.x;
            if(pos.x > this.roomBounds.x) pos.x = this.roomBounds.x;
            if(pos.z < -this.roomBounds.z) pos.z = -this.roomBounds.z;
            if(pos.z > this.roomBounds.z) pos.z = this.roomBounds.z;
            pos.y = 4; // keep height fixed
            
            // Footsteps
            if((Math.abs(this.velocity.x) > 1 || Math.abs(this.velocity.z) > 1) && Math.random() < 0.1) {
                this.audio.playFootstep();
            }
            
            // Raycast for UI prompt
            this.raycaster.setFromCamera(this.center, this.camera);
            const intersects = this.raycaster.intersectObjects(this.interactables);
            const prompt = document.getElementById('interaction-prompt');
            if (intersects.length > 0 && intersects[0].distance < 6) {
                prompt.classList.remove('hidden');
            } else {
                prompt.classList.add('hidden');
            }
            
            // Light flicker
            if(this.mainLight && Math.random() < 0.05) {
                this.mainLight.intensity = 0.8 + Math.random() * 0.4;
            }
        }
        
        this.prevTime = time;
        this.renderer.render(this.scene, this.camera);
    }
}

window.onload = () => { new Game(); };
"""

# 5. Write files to disk
with open(os.path.join(GAME_DIR, 'index.html'), 'w') as f:
    f.write(html_content)
with open(os.path.join(GAME_DIR, 'style.css'), 'w') as f:
    f.write(css_content)
with open(os.path.join(GAME_DIR, 'game.js'), 'w') as f:
    f.write(js_content)

# 6. Start Server in Background
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=GAME_DIR, **kwargs)

    def log_message(self, format, *args):
        pass # Suppress logging

PORT = 8000
Handler = CustomHandler

# Ensure we don't start multiple servers if cell is run multiple times
def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

# Only start the thread if the port isn't already in use
try:
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    print("Game server started.")
except Exception as e:
    print(f"Server might already be running: {e}")

# 7. Provide Native Colab URL
print("\n" + "="*60)
print(" HOSPITAL TREASURE HUNT GAME IS READY!")
print(" Click the link below to open the game in a new browser tab:")
print("="*60 + "\n")
output.serve_kernel_port_as_window(PORT, path='/index.html')