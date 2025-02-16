// import AgoraRTC from "agora-rtc-sdk-ng";

const AgoraRTC = require("agora-rtc-sdk-ng");

// RTC client instance
let client = null;

// Declare variables for the local tracks
let localAudioTrack = null; 
let localVideoTrack = null; 

// TODO: cancel later
const appId = "ceda308b561b422c9e82e8261a3f00ba";
const channel = "testchannel";
const token = "007eJxTYFj0QPX2RpPZPELxTIUhbWc8FTy+LZnvX9+hp9DkcFjs8HYFhuTUlERjA4skUzPDJBMjo2TLVAsjIDIzTDROMzBISgxctDG9IZCRgWPpGiZGBggE8bkZSlKLS5IzEvPyUnMYGADFlSEM";
const uid = 123; // User ID

// Initialize the AgoraRTC client
function initializeClient() {
    client = AgoraRTC.createClient({ mode: "rtc", codec: "vp8" });
    setupEventListeners();
}

// Handle client events
function setupEventListeners() {
    client.on("user-published", async (user, mediaType) => {
        await client.subscribe(user, mediaType);
        console.log("subscribe success");

        if (mediaType === "video") {
            displayRemoteVideo(user);
        }

        if (mediaType === "audio") {
            user.audioTrack.play();
        }
    });

    client.on("user-unpublished", (user) => {
        const remotePlayerContainer = document.getElementById(user.uid);
        remotePlayerContainer?.remove();
    });
}

// Join a channel and publish local media
async function joinChannel() {
    console.log("joining channel");
    await client.join(appId, channel, token, uid);
    await createLocalTracks();
    await publishLocalTracks();
    displayLocalVideo();
    console.log("Publish success!");
}

// Create local audio and video tracks
async function createLocalTracks() {
    localAudioTrack = await AgoraRTC.createMicrophoneAudioTrack();
    localVideoTrack = await AgoraRTC.createCameraVideoTrack();
}

// Publish local audio and video tracks
async function publishLocalTracks() {
    await client.publish([localAudioTrack, localVideoTrack]);
}

// Display local video
function displayLocalVideo() {
    const localPlayerContainer = document.createElement("div");
    localPlayerContainer.id = uid;
    localPlayerContainer.textContent = `Local user ${uid}`;
    localPlayerContainer.style.width = "100%";
    localPlayerContainer.style.height = "100%";
    document.getElementById('local-video-container').appendChild(localPlayerContainer);
    localVideoTrack.play(localPlayerContainer);
}

// Display remote video
function displayRemoteVideo(user) {
    const remoteVideoTrack = user.videoTrack;
    const remotePlayerContainer = document.createElement("div");
    remotePlayerContainer.id = user.uid.toString();
    remotePlayerContainer.textContent = `Remote user ${user.uid}`;
    remotePlayerContainer.style.width = "100%";
    remotePlayerContainer.style.height = "100%";
    document.getElementById('remote-video-container').appendChild(remotePlayerContainer);
    remoteVideoTrack.play(remotePlayerContainer);
}

// Add these new functions at the top level of the file
function showVideoCall() {
    document.getElementById('callContainer').style.display = 'none';
    document.getElementById('agora-call').style.display = 'block';
    // Assuming there's a function to mute Tavus avatar
    if (typeof window.muteTavusAudio === 'function') {
        window.muteTavusAudio();
    }
}

function hideVideoCall() {
    document.getElementById('callContainer').style.display = 'block';
    document.getElementById('agora-call').style.display = 'none';
    // Assuming there's a function to unmute Tavus avatar
    if (typeof window.unmuteTavusAudio === 'function') {
        window.unmuteTavusAudio();
    }
}

// Modify the leaveChannel function
async function leaveChannel() {
    // Close local tracks
    localAudioTrack.close();
    localVideoTrack.close();

    // Remove local video container
    const localPlayerContainer = document.getElementById(uid);
    localPlayerContainer?.remove();
    // Remove all remote video containers
    for (const user of client.remoteUsers) {
        const playerContainer = document.getElementById(user.uid);
        playerContainer?.remove();
    }

    // Leave the channel
    await client.leave();
}

// Initialize when join button is clicked
document.getElementById("join-videocall").onclick = async () => {
    if (!client) {
        initializeClient();
    }
    await joinChannel();
};

document.getElementById("leave-videocall").onclick = leaveChannel;

window.ipcRenderer.on('webhook-event',async (event, data) => {
    console.log(data.serviceName, 'chat');
    // hide call container
    document.getElementById('callContainer').style.display = 'none';
    window.daily.leave()
    // end the conversation
    window.ipcRenderer.send('end-conversation', {
        conversationId: window.conversationId,
        token: "a335c04a5be24585af0ddae7e08c40e5"
    });

    // show agora call container
    document.getElementById('agora-call').style.display = 'block';
    if (!client) {
        initializeClient();
    }
    await joinChannel();
});