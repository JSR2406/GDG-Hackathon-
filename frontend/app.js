// Determine API Base URL
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000/api/v1'
    : 'https://eco-sync-mvp.vercel.app/api/v1'; // Explicit Production URL

// ...

// FIX IMAGE DISPLAY (Line 374 approx)
// In loadLostFoundItems:
// ${item.photo_url ? `<img src="${item.photo_url.startsWith('http') ? item.photo_url : (API_BASE.replace('/api/v1','') + item.photo_url)}" ...` : ''}

// Wait, API_BASE ending in /api/v1 might complicate image fetching if images are at /uploads.
// Backend returns "/uploads/filename".
// We need "https://site.com/uploads/filename" if served statically?
// Or "https://site.com/api/v1/uploads..."? No static files are usually root or specific static dir.
// My Vercel config maps /api/ to backend.
// It maps / to frontend.
// It does NOT map /uploads.
// I need to serve /uploads via FastAPI or Vercel config.
// Currently main.py mounts static: app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
// This means access is at `HOST/uploads/...` directly? Or `HOST/api/v1/uploads`?
// main.py mount is on ROOT `app.mount`.
// But Vercel routes `/api/*` to `main.py`.
// If I request `https://site/api/uploads/xyz` -> `main.py` handles it.
// `app.mount("/uploads")` -> URL is `/uploads`.
// So inside Vercel, `main.py` sees path `/uploads`.
// So the request should be `https://site/api/uploads/xyz`? 
// The Vercel route strips `/api/`? No, usually passing full path.

// Let's assume on Vercel:
// Request: /api/uploads/file.jpg -> main.py -> app
// app has route /uploads.
// So usage: `${API_BASE.replace('/v1', '')}${item.photo_url}`
// API_BASE = .../api/v1
// item.photo_url = /uploads/file.jpg
// Result: .../api/uploads/file.jpg. 

// Let's update loadLostFoundItems to use this logic.
async function loadLostFoundItems() {
    try {
        const response = await fetch(`${API_BASE}/lost-found/`);
        const items = await response.json();
        const container = document.getElementById('lostFoundList');

        const baseUrl = API_BASE.replace('/api/v1', ''); // http://loc:8000 or https://site

        container.innerHTML = items.map(item => `
            <div class="grid-card">
                 ${item.photo_url ? `<img src="${item.photo_url.startsWith('http') ? item.photo_url : (baseUrl + item.photo_url)}" alt="${item.item_name}" style="width:100%; height:150px; object-fit:cover; border-radius:8px;">` : ''}
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                     <span style="background:${item.type === 'lost' ? '#fee2e2' : '#d1fae5'}; color:${item.type === 'lost' ? '#b91c1c' : '#065f46'}; padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:700; text-transform:uppercase;">${item.type}</span>
                     <span style="font-size:0.8rem; color:#6b7280;">${new Date(item.created_at).toLocaleDateString()}</span>
                </div>
                <h4 style="margin-bottom:4px;">${item.item_name}</h4>
                <p style="font-size:0.9rem; color:#4b5563;">${item.description || ''}</p>
            </div>
        `).join('');
    } catch (err) { console.error(err); }
}

// --- VISUAL EFFECTS ---
function triggerConfetti() {
    const colors = ['#059669', '#10b981', '#34d399', '#6ee7b7'];
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        Object.assign(particle.style, {
            position: 'fixed', left: '50%', top: '50%', width: '8px', height: '8px',
            backgroundColor: colors[Math.floor(Math.random() * colors.length)],
            borderRadius: '50%', pointerEvents: 'none', zIndex: '9999'
        });
        document.body.appendChild(particle);

        const angle = Math.random() * Math.PI * 2;
        const velocity = 5 + Math.random() * 10;
        const tx = Math.cos(angle) * 200 * (Math.random() + 0.5);
        const ty = Math.sin(angle) * 200 * (Math.random() + 0.5);

        particle.animate([
            { transform: 'translate(0,0)' },
            { transform: `translate(${tx}px, ${ty}px) scale(0)`, opacity: 0 }
        ], { duration: 1000 + Math.random() * 500, easing: 'cubic-bezier(0, .9, .57, 1)', fill: 'forwards' });
        setTimeout(() => particle.remove(), 1600);
    }
}

// --- AUTH LOGIC ---

let CURRENT_USER = null;

function toggleAuth(mode) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');

    if (mode === 'login') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        tabLogin.classList.remove('active');
        tabRegister.classList.add('active');
    }
}

function updateAuthState(user) {
    CURRENT_USER = user;
    localStorage.setItem('currentUser', JSON.stringify(user));

    // Update Header
    const headerProfile = document.getElementById('headerProfile');
    const headerName = document.getElementById('headerName');
    headerProfile.style.display = 'flex';
    headerName.textContent = user.name;

    // Auto-populate Dropdowns (Simulate 'My Account')
    const selects = ['userSelectUpload', 'userSelectBarter', 'userSelectMatches', 'lostFoundUserId'];
    selects.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            // If option exists, select it
            // Logic: populateUserSelects() is called separately, we just set value
            // We use a small timeout to ensure options are loaded
            setTimeout(() => { if ([...el.options].some(o => o.value == user.id)) el.value = user.id; }, 500);
        }
    });

    console.log("Logged in as:", user.name);
}

document.addEventListener('DOMContentLoaded', () => {
    populateUserSelects().then(() => {
        // Restore session
        const stored = localStorage.getItem('currentUser');
        if (stored) updateAuthState(JSON.parse(stored));
    });
});

// --- API & FORMS ---

async function populateUserSelects() {
    try {
        let response = await fetch(`${API_BASE}/users/`);
        if (!response.ok) throw new Error('Failed to fetch users');
        let users = await response.json();

        // AUTO-SEED if empty (for Vercel Demo)
        if (users.length === 0) {
            console.log("Empty DB detected. Seeding Demo Users...");
            const demoUsers = [
                { name: "Alice Logistics", email: "alice@corp.com", semester: 1, department: "Logistics", hostel: "Block A" },
                { name: "Bob IT Solutions", email: "bob@tech.com", semester: 2, department: "IT", hostel: "Block B" },
                { name: "Charlie Sales", email: "charlie@sales.com", semester: 3, department: "Sales", hostel: "Block C" }
            ];

            await Promise.all(demoUsers.map(u =>
                fetch(`${API_BASE}/users/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(u) })
            ));

            // Re-fetch
            response = await fetch(`${API_BASE}/users/`);
            users = await response.json();
        }

        const selects = ['userSelectUpload', 'userSelectBarter', 'userSelectMatches', 'lostFoundUserId'];
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (!select) return;
            select.innerHTML = '<option value="">Select Profile (Demo)</option>';
            users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = `${user.name} (${user.department})`;
                select.appendChild(option);
            });
        });
    } catch (error) { console.error('Error loading users:', error); }
}

// LOGIN Handler
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const btn = document.getElementById('loginBtn');
    const respDiv = document.getElementById('loginResponse');

    btn.disabled = true; btn.textContent = "Verifying...";
    respDiv.innerHTML = "";

    try {
        // Fetch all users to find match (Mock Auth)
        const res = await fetch(`${API_BASE}/users/`);
        if (!res.ok) throw new Error('API Error');
        const users = await res.json();

        const found = users.find(u => u.email.toLowerCase() === email.toLowerCase());

        if (found) {
            triggerConfetti();
            updateAuthState(found);
            respDiv.innerHTML = `<div style="color:var(--success);">✅ Success! Redirecting...</div>`;
            setTimeout(() => switchTab('landing'), 1000);
        } else {
            respDiv.innerHTML = `<div style="color:var(--error);">❌ User not found. Please register.</div>`;
        }
    } catch (err) {
        respDiv.innerHTML = `<div style="color:var(--error);">❌ Error connecting to server.</div>`;
    } finally {
        btn.disabled = false; btn.textContent = "Secure Login";
    }
});

// REGISTER Handler
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById('fullName').value,
        email: document.getElementById('email').value,
        semester: parseInt(document.getElementById('semester').value),
        department: document.getElementById('department').value,
        hostel: document.getElementById('hostel').value
    };
    try {
        const response = await fetch(`${API_BASE}/users/`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        const result = await response.json();
        const div = document.getElementById('registerResponse');
        if (response.ok) {
            triggerConfetti();
            div.innerHTML = `<div style="color: var(--success); font-weight: 600;">✅ Account Created!</div>`;
            await populateUserSelects();
            updateAuthState(result);
            setTimeout(() => switchTab('landing'), 1500);
        } else {
            // Handle 'Email exists' 400
            if (response.status === 400 && result.detail === "Email already registered") {
                div.innerHTML = `<div style="color: var(--warning);">⚠️ Email exists. Please Login.</div>`;
            } else {
                div.innerHTML = `<div style="color: var(--error);">❌ Error: ${result.detail}</div>`;
            }
        }
    } catch (err) { console.error(err); }
});

// Demo User Handler
async function loginDemoUser() {
    const btn = document.getElementById('demoLoginBtn');
    if (btn) { btn.disabled = true; btn.textContent = "Setting up Demo..."; }

    const demoUser = {
        name: "Demo Creator",
        email: "demo@ecosync.com",
        semester: 4,
        department: "Product",
        hostel: "Innovation Lab"
    };

    try {
        // Try creating (or getting if exists)
        let res = await fetch(`${API_BASE}/users/`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(demoUser)
        });

        // If 400, it exists. Fetch all users to find ID.
        if (res.status === 400) {
            const all = await (await fetch(`${API_BASE}/users/`)).json();
            const found = all.find(u => u.email === demoUser.email);
            if (found) {
                triggerConfetti();
                updateAuthState(found);
                setTimeout(() => switchTab('landing'), 500);
                return;
            }
        }

        if (res.ok) {
            const user = await res.json();
            triggerConfetti();
            updateAuthState(user);
            setTimeout(() => switchTab('landing'), 500);
        } else {
            alert("Demo Login Failed: " + res.statusText);
        }
    } catch (e) { console.error(e); alert("Error: " + e.message); }
    finally { if (btn) { btn.disabled = false; btn.textContent = "🚀 Launch Demo Profile"; } }
}
// Demo Photo Logic
async function useDemoPhoto(type = 'laptop') {
    const fileNameDisplay = document.getElementById('file-name');
    if (fileNameDisplay) fileNameDisplay.textContent = "Loading sample image...";

    const urls = {
        'laptop': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&q=80',
        'book': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&q=80',
        'calc': 'https://images.unsplash.com/photo-1574607383476-f517b260d35b?w=500&q=80'
    };

    try {
        // Fetch sample
        const res = await fetch(urls[type]);
        const blob = await res.blob();
        const file = new File([blob], `demo_${type}.jpg`, { type: "image/jpeg" });

        // Populate inputs
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        document.getElementById('itemPhoto').files = dataTransfer.files;
        if (fileNameDisplay) fileNameDisplay.textContent = `Selected: demo_${type}.jpg (Ready to Analyze)`;

    } catch (e) { alert("Failed to load demo photo: " + e.message); }
}

document.getElementById('uploadItemForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userId = document.getElementById('userSelectUpload').value;
    const fileInput = document.getElementById('itemPhoto');
    if (!userId || !fileInput.files[0]) { alert("Please select user and file!"); return; }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const btn = document.getElementById('uploadBtn');
    btn.disabled = true; btn.textContent = 'Processing...';

    try {
        const response = await fetch(`${API_BASE}/items/users/${userId}/items/upload-photo`, { method: 'POST', body: formData });
        const result = await response.json();
        const div = document.getElementById('uploadResponse');

        if (response.ok) {
            triggerConfetti();
            div.innerHTML = `
                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <h3 style="margin:0; color:#111827;">${result.item.name}</h3>
                        <span style="background:#d1fae5; color:#065f46; padding:4px 8px; border-radius:4px; font-size:0.8rem; font-weight:600;">Confidence: ${(result.analysis.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <p style="color:#6b7280; font-size:0.9rem; margin-bottom:12px;">${result.analysis.description || 'No description.'}</p>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:0.9rem;">
                        <div>🏷️ ${result.item.category}</div>
                        <div>✨ ${result.item.condition}</div>
                        <div style="color: var(--success);">🌿 Eco-Score: ${result.analysis.eco_value}/10</div>
                    </div>
                </div>`;
            e.target.reset(); document.getElementById('file-name').textContent = '';
            // Reselect user
            document.getElementById('userSelectUpload').value = CURRENT_USER ? CURRENT_USER.id : "";
        } else div.innerHTML = `<div style="color: var(--error);">❌ Error: ${result.detail}</div>`;
    } catch (err) { alert(err.message); } finally { btn.disabled = false; btn.textContent = 'Analyze & List Asset'; }
});

// Barter Intent
document.getElementById('barterIntentForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userId = document.getElementById('userSelectBarter').value;
    const data = {
        item_id: parseInt(document.getElementById('itemSelectBarter').value),
        want_category: document.getElementById('wantCategory').value,
        want_description: document.getElementById('description').value,
        emergency: document.getElementById('isEmergency').checked
    };
    try {
        const response = await fetch(`${API_BASE}/barter/barter-intents?user_id=${userId}`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        const result = await response.json();
        const div = document.getElementById('barterResponse');
        if (response.ok) {
            div.innerHTML = result.match_found ?
                `<div style="background:#d1fae5; padding:16px; border-radius:8px; color:#065f46; border:1px solid #10b981;"><strong>🎉 MATCH FOUND!</strong><br>View Details in 'Matches' tab.</div>` :
                `<div style="background:#eff6ff; padding:16px; border-radius:8px; color:#1e40af; border:1px solid #3b82f6;">✅ Intent Posted. We'll search for matches.</div>`;
            if (result.match_found) triggerConfetti();
            e.target.reset();
            document.getElementById('userSelectBarter').value = CURRENT_USER ? CURRENT_USER.id : "";
        } else div.innerHTML = `<div style="color: var(--error);">❌ Error: ${result.detail}</div>`;
    } catch (err) { console.error(err); }
});

// LOST & FOUND LOGIC
document.getElementById('lostFoundForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userId = document.getElementById('lostFoundUserId').value;
    const fileInput = document.getElementById('lostFoundPhoto');

    let photoUrl = null;
    if (fileInput.files[0]) {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        const uploadRes = await fetch(`${API_BASE}/lost-found/upload`, { method: 'POST', body: formData });
        if (uploadRes.ok) photoUrl = (await uploadRes.json()).photo_url;
    }

    const data = {
        item_name: document.getElementById('lostFoundItemName').value,
        category: document.getElementById('lostFoundCategory').value,
        description: document.getElementById('lostFoundDescription').value,
        type: document.getElementById('lostFoundType').value,
        photo_url: photoUrl
    };

    try {
        const response = await fetch(`${API_BASE}/lost-found/?user_id=${userId}`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (response.ok) {
            document.getElementById('lostFoundResponse').className = 'response success';
            document.getElementById('lostFoundResponse').textContent = `✅ Report Submitted!`;
            e.target.reset(); document.getElementById('lf-file-name').textContent = '';
            loadLostFoundItems();
            document.getElementById('lostFoundUserId').value = CURRENT_USER ? CURRENT_USER.id : "";
        } else {
            document.getElementById('lostFoundResponse').textContent = `❌ Error`;
        }
    } catch (error) { console.error(error); }
});

async function loadLostFoundItems() {
    try {
        const response = await fetch(`${API_BASE}/lost-found/`);
        const items = await response.json();
        const container = document.getElementById('lostFoundList');

        const baseUrl = API_BASE.replace('/api/v1', ''); // http://loc:8000 or https://site

        container.innerHTML = items.map(item => `
            <div class="grid-card">
                 ${item.photo_url ? `<img src="${item.photo_url.startsWith('http') ? item.photo_url : (baseUrl + item.photo_url)}" alt="${item.item_name}" style="width:100%; height:150px; object-fit:cover; border-radius:8px;">` : ''}
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                     <span style="background:${item.type === 'lost' ? '#fee2e2' : '#d1fae5'}; color:${item.type === 'lost' ? '#b91c1c' : '#065f46'}; padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:700; text-transform:uppercase;">${item.type}</span>
                     <span style="font-size:0.8rem; color:#6b7280;">${new Date(item.created_at).toLocaleDateString()}</span>
                </div>
                <h4 style="margin-bottom:4px;">${item.item_name}</h4>
                <p style="font-size:0.9rem; color:#4b5563;">${item.description || ''}</p>
            </div>
        `).join('');
    } catch (err) { console.error(err); }
}

// Helper: Populate item select when user changes (for Barter)
document.getElementById('userSelectBarter')?.addEventListener('change', async (e) => {
    const userId = e.target.value;
    if (!userId) return;
    const res = await fetch(`${API_BASE}/items/users/${userId}/items`);
    const items = await res.json();
    const select = document.getElementById('itemSelectBarter');
    select.innerHTML = '<option value="">Select Asset</option>';
    items.forEach(i => {
        const opt = document.createElement('option');
        opt.value = i.id; opt.textContent = i.name; select.appendChild(opt);
    });
});

async function loadMatches() {
    const userId = document.getElementById('userSelectMatches').value;
    const res = await fetch(`${API_BASE}/matches/${userId}`);
    const matches = await res.json();
    document.getElementById('matchesList').innerHTML = matches.map(m => `
        <div class="glass-panel" style="margin-bottom:16px;">
            <div style="font-weight:700; color:#1f2937;">${m.type === 'three_way' ? 'Statement Cycle' : 'Direct Swap'}</div>
            <div>${m.participants.map(p => `<div>${p.user_name} ➔ ${p.wants}</div>`).join('')}</div>
            ${m.status === 'pending' ? `<button class="btn-primary" onclick="acceptMatch(${m.id}, ${userId})">Authorize</button>` : ''}
        </div>
    `).join('');
}

async function acceptMatch(mid, uid) {
    const res = await fetch(`${API_BASE}/matches/${mid}/accept?user_id=${uid}`, { method: 'POST' });
    if (res.ok) { triggerConfetti(); loadMatches(); }
}

async function loadLeaderboard() {
    const res = await fetch(`${API_BASE}/eco-credits/leaderboard/top`);
    const data = await res.json();
    document.getElementById('leaderboardList').innerHTML = data.map(entry => `
        <div style="display:flex; align-items:center; padding:12px; border-bottom:1px solid #f3f4f6;">
            <div style="font-weight:700;">#${entry.rank}</div>
            <div style="flex:1; margin-left:12px;">${entry.user_name}</div>
            <div style="font-WEIGHT:700; color:var(--primary);">${entry.total_eco_credits}</div>
        </div>
    `).join('');
}

// --- TEST HELPERS ---
window.fillLF = function (type, item, cat, desc) {
    document.getElementById('lostFoundType').value = type;
    document.getElementById('lostFoundItemName').value = item;
    document.getElementById('lostFoundCategory').value = cat;
    document.getElementById('lostFoundDescription').value = desc;
};

window.fillBarter = function (cat, desc, emergency) {
    document.getElementById('wantCategory').value = cat;
    document.getElementById('description').value = desc;
    document.getElementById('isEmergency').checked = emergency;
};

window.selectReporter = function (namePartial) {
    const select = document.getElementById('lostFoundUserId');
    for (let i = 0; i < select.options.length; i++) {
        if (select.options[i].text.includes(namePartial)) {
            select.selectedIndex = i;
            break;
        }
    }
};
