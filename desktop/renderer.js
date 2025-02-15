const { ipcRenderer } = require('electron');
const DailyIframe = require('@daily-co/daily-js');
const { createRoot } = require('react-dom/client');

let daily = null;
let currentConversation = null;
let token = '';

// WebGL shader sources
const vertexShaderSource = `
    attribute vec2 a_position;
    attribute vec2 a_texCoord;
    varying vec2 v_texCoord;
    void main() {
        gl_Position = vec4(a_position, 0, 1);
        v_texCoord = vec2(a_texCoord.x, 1.0 - a_texCoord.y);
    }
`;

const fragmentShaderSource = `
    precision mediump float;
    uniform sampler2D u_image;
    varying vec2 v_texCoord;
    uniform vec3 u_keyColor;
    uniform float u_threshold;
    void main() {
        vec4 color = texture2D(u_image, v_texCoord);
        float diff = length(color.rgb - u_keyColor);
        gl_FragColor = diff < u_threshold ? vec4(0.0) : color;
    }
`;

// Initialize WebGL context and resources
function initWebGL(gl) {
    const program = gl.createProgram();
    
    // Create and compile vertex shader
    const vertexShader = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vertexShader, vertexShaderSource);
    gl.compileShader(vertexShader);
    
    // Create and compile fragment shader
    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fragmentShader, fragmentShaderSource);
    gl.compileShader(fragmentShader);
    
    // Link program
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    gl.useProgram(program);

    // Set up position buffer
    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]),
        gl.STATIC_DRAW
    );

    // Set up texture coordinate buffer
    const texCoordBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, texCoordBuffer);
    gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array([0, 0, 1, 0, 0, 1, 1, 1]),
        gl.STATIC_DRAW
    );

    // Connect attributes
    const positionLocation = gl.getAttribLocation(program, "a_position");
    const texCoordLocation = gl.getAttribLocation(program, "a_texCoord");

    gl.enableVertexAttribArray(positionLocation);
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    gl.enableVertexAttribArray(texCoordLocation);
    gl.bindBuffer(gl.ARRAY_BUFFER, texCoordBuffer);
    gl.vertexAttribPointer(texCoordLocation, 2, gl.FLOAT, false, 0, 0);

    // Create and set up texture
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);

    return {
        program,
        texture,
        imageLocation: gl.getUniformLocation(program, "u_image"),
        keyColorLocation: gl.getUniformLocation(program, "u_keyColor"),
        thresholdLocation: gl.getUniformLocation(program, "u_threshold")
    };
}

// Set up video processing with WebGL
function setupVideoProcessing() {
    const video = document.getElementById('videoElement');
    const canvas = document.getElementById('outputCanvas');
    const gl = canvas.getContext('webgl', {
        premultipliedAlpha: false,
        alpha: true
    });

    if (!gl) {
        console.error('WebGL not supported');
        return;
    }

    const webGLContext = initWebGL(gl);
    let animationFrameId;
    let lastFrameTime = 0;
    const targetFPS = 30;
    const frameInterval = 1000 / targetFPS;

    function processFrame(currentTime) {
        if (currentTime - lastFrameTime < frameInterval) {
            animationFrameId = requestAnimationFrame(processFrame);
            return;
        }

        lastFrameTime = currentTime;

        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            gl.viewport(0, 0, canvas.width, canvas.height);

            gl.bindTexture(gl.TEXTURE_2D, webGLContext.texture);
            gl.texImage2D(
                gl.TEXTURE_2D,
                0,
                gl.RGBA,
                gl.RGBA,
                gl.UNSIGNED_BYTE,
                video
            );

            gl.uniform1i(webGLContext.imageLocation, 0);
            gl.uniform3f(webGLContext.keyColorLocation, 0/255, 255/255, 155/255);
            gl.uniform1f(webGLContext.thresholdLocation, 0.85);

            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        }

        animationFrameId = requestAnimationFrame(processFrame);
    }

    processFrame(0);

    return () => {
        cancelAnimationFrame(animationFrameId);
        if (gl && webGLContext.program && webGLContext.texture) {
            gl.deleteProgram(webGLContext.program);
            gl.deleteTexture(webGLContext.texture);
        }
    };
}

// Event Handlers
async function startCall() {
    token = "a335c04a5be24585af0ddae7e08c40e5";

    try {
        // Create Daily room
        // document.getElementById('startButton').disabled = true;
        // document.getElementById('startButton').textContent = 'Loading...';
        
        currentConversation = await ipcRenderer.invoke('create-conversation', token);


        ipcRenderer.on('webhook-event', (event, data) => {
            console.log(data, event)
            // Update UI elements
            document.getElementById('status').innerHTML = data.status
            document.getElementById('message').innerHTML = data.message
          })

        // Initialize Daily.co
        daily = DailyIframe.createCallObject();
        
        // Join the call
        await daily.join({ url: currentConversation.conversation_url });
        
        // Show call container and hide token form
        // document.getElementById('tokenForm').style.display = 'none';
        // document.getElementById('callContainer').style.display = 'block';
        
        // Set up video processing
        setupVideoProcessing();
        
        // Set up Daily event listeners
        daily.on('participant-joined', handleParticipantJoined);
        daily.on('participant-left', handleParticipantLeft);
        
        // Listen for track-started events
        daily.on('track-started', (evt) => {
            if (!evt.participant.local) {
                if (evt.track.kind === 'video') {
                    const video = document.getElementById('videoElement');
                    const stream = new MediaStream([evt.track]);
                    video.srcObject = stream;
                    video.play().catch(console.error);
                } else if (evt.track.kind === 'audio') {
                    let audioElement = document.getElementById(`audio-${evt.participant.session_id}`);
                    if (!audioElement) {
                        audioElement = document.createElement('audio');
                        audioElement.id = `audio-${evt.participant.session_id}`;
                        audioElement.autoplay = true;
                        document.body.appendChild(audioElement);
                    }
                    const audioStream = new MediaStream([evt.track]);
                    audioElement.srcObject = audioStream;
                }
            }
        });
        
    } catch (error) {
        alert(`Failed to join the call: ${error.message}`);
        // document.getElementById('startButton').disabled = false;
        // document.getElementById('startButton').textContent = 'Start Video Call';
    }
}

function handleParticipantJoined(event) {
    const participant = event.participant;
    if (!participant.local) {
        // Get the video element
        const video = document.getElementById('videoElement');
        
        // Create audio element if it doesn't exist
        let audioElement = document.getElementById(`audio-${participant.session_id}`);
        if (!audioElement) {
            audioElement = document.createElement('audio');
            audioElement.id = `audio-${participant.session_id}`;
            audioElement.autoplay = true;
            document.body.appendChild(audioElement);
        }
        
        // Handle audio track if available
        if (participant.tracks && participant.tracks.audio && participant.tracks.audio.track) {
            const audioStream = new MediaStream([participant.tracks.audio.track]);
            audioElement.srcObject = audioStream;
        }
        
        // Handle video track if available
        if (participant.tracks && participant.tracks.video && participant.tracks.video.track) {
            const videoStream = new MediaStream([participant.tracks.video.track]);
            video.srcObject = videoStream;
            video.play().catch(console.error);
        } else {
            console.log('Waiting for video track...');
        }
    }
}

function handleParticipantLeft(event) {
    const participant = event.participant;
    if (!participant.local) {
        // Clear video
        const video = document.getElementById('videoElement');
        if (video) {
            video.srcObject = null;
        }
        
        // Remove audio element
        const audioElement = document.getElementById(`audio-${participant.session_id}`);
        if (audioElement) {
            audioElement.srcObject = null;
            audioElement.remove();
        }
    }
}

async function handleLeaveCall() {
    if (daily) {
        await daily.leave();
        if (currentConversation) {
            await ipcRenderer.invoke('end-conversation', {
                conversationId: currentConversation.conversation_id,
                token
            });
        }
        daily = null;
        currentConversation = null;
        
        // Reset UI
        document.getElementById('callContainer').style.display = 'none';
        document.getElementById('startForm').style.display = 'flex';
        document.getElementById('startButton').disabled = false;
        document.getElementById('startButton').textContent = 'Start Video Call';
    }
}

function toggleMicrophone() {
    if (daily) {
        const audioState = daily.localAudio();
        daily.setLocalAudio(!audioState);
        document.getElementById('toggleMic').textContent = !audioState ? 'Mic is On' : 'Mic is Off';
    }
}

// Event Listeners
document.getElementById('leaveCall').addEventListener('click', handleLeaveCall);
document.getElementById('toggleMic').addEventListener('click', toggleMicrophone);
document.getElementById('startButton').addEventListener('click', async () => {
    const startButton = document.getElementById('startButton');
    const startForm = document.getElementById('startForm');
    const callContainer = document.getElementById('callContainer');
    
    startButton.disabled = true;
    startButton.textContent = 'Loading...';
    
    try {
        await startCall();
        startForm.style.display = 'none';
        callContainer.style.display = 'block';
    } catch (error) {
        console.error('Failed to start call:', error);
        startButton.disabled = false;
        startButton.textContent = 'Start Video Call';
        alert('Failed to start call: ' + error.message);
    }
});

// Cleanup on window unload
window.addEventListener('unload', () => {
    if (daily) {
        daily.leave();
    }
});
