// Test - replace TEST_SCORE with the actual score instead of a constant
const TEST_SCORE = 95; 

const sign = TEST_SCORE > 75 ? "🛑" : TEST_SCORE >= 40 ? "⚠️" : "✅";
const color = TEST_SCORE > 75 ? "#d93025" : TEST_SCORE >= 40 ? "#f2994a" : "#188038";

// Animation
document.head.insertAdjacentHTML('beforeend', `<style>
    @keyframes wave {
        0% { box-shadow: 0 0 0 0 #d93025cc; }
        70% { box-shadow: 0 0 0 25px #d9302500; }
        100% { box-shadow: 0 0 0 0 #d9302500; }
    }
    .pulsing-alert { animation: wave 1.4s infinite ease-in-out; }
</style>`);

// Button
const box = document.createElement('button');
box.style.cssText = `
    position: fixed; inset: auto 25px 25px auto; z-index: 999999;
    width: 100px; aspect-ratio: 1; border-radius: 50%;
    background: #fff; border: 4px solid ${color};
    display: grid; place-items: center; font-size: 55px; cursor: pointer; /* Changed none to grid so it is visible */
`;

box.textContent = sign;

// Pulse
if (TEST_SCORE > 75) box.className = "pulsing-alert";

document.body.appendChild(box);
