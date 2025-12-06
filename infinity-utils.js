/**
 * Infinity Portal Utilities
 * JavaScript utilities for GitHub integration, encryption, and authentication
 */

// ============================================================================
// Encryption & Security
// ============================================================================

/**
 * Dual-AI encryption function
 * Uses two AI-generated salt components for enhanced security
 */
async function dualAIEncrypt(obj, pass) {
  const ai1 = crypto.getRandomValues(new Uint8Array(8));
  const ai2 = crypto.getRandomValues(new Uint8Array(8));
  const salt = new Uint8Array([...ai1, ...ai2]);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await deriveKey(pass + btoa(ai1.join('')) + btoa(ai2.join('')), salt);
  const ct = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv }, 
    key, 
    new TextEncoder().encode(JSON.stringify(obj))
  );
  return { 
    salt: u8ToB64(salt), 
    iv: u8ToB64(iv), 
    ct: u8ToB64(new Uint8Array(ct)) 
  };
}

/**
 * Dual-AI decryption function
 */
async function dualAIDecrypt(encData, pass) {
  const salt = b64ToU8(encData.salt);
  const iv = b64ToU8(encData.iv);
  const ct = b64ToU8(encData.ct);
  
  const ai1 = salt.slice(0, 8);
  const ai2 = salt.slice(8, 16);
  
  const key = await deriveKey(pass + btoa(ai1.join('')) + btoa(ai2.join('')), salt);
  const decrypted = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv }, 
    key, 
    ct
  );
  return JSON.parse(new TextDecoder().decode(decrypted));
}

/**
 * Derive encryption key from password and salt
 */
async function deriveKey(password, salt) {
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    { name: "PBKDF2" },
    false,
    ["deriveKey"]
  );
  
  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: salt,
      iterations: 100000,
      hash: "SHA-256"
    },
    keyMaterial,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"]
  );
}

/**
 * Convert Uint8Array to base64
 */
function u8ToB64(arr) {
  return btoa(String.fromCharCode.apply(null, arr));
}

/**
 * Convert base64 to Uint8Array
 */
function b64ToU8(str) {
  return new Uint8Array(atob(str).split('').map(c => c.charCodeAt(0)));
}

// ============================================================================
// GitHub Integration
// ============================================================================

/**
 * Get GitHub token from session storage
 */
function getToken() {
  return sessionStorage.getItem('github_token') || '';
}

/**
 * Set GitHub token in session storage
 */
function setToken(token) {
  sessionStorage.setItem('github_token', token);
}

/**
 * Rogers AI GitHub search function
 * Searches code in a repository using GitHub API
 */
async function rogersRespond(query, owner = 'pewpi-infinity', repo = 'mongoose.os') {
  const token = getToken();
  if (!token) {
    return {
      error: true,
      message: "(no GitHub token in memory)"
    };
  }
  
  try {
    const resp = await fetch(
      `https://api.github.com/search/code?q=${encodeURIComponent(query)}+in:file+repo:${owner}/${repo}`,
      {
        headers: { 
          Authorization: `token ${token}`,
          Accept: 'application/vnd.github+json'
        }
      }
    );
    const data = await resp.json();
    return {
      error: false,
      items: data.items?.slice(0, 5) || [],
      total_count: data.total_count || 0
    };
  } catch (err) {
    return {
      error: true,
      message: err.message
    };
  }
}

/**
 * Commit file to GitHub repository
 */
async function commitToGitHub(owner, repo, path, branch, message, content) {
  const token = getToken();
  if (!token) {
    throw new Error('GitHub token not found');
  }
  
  const baseUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;
  
  // Get current file SHA if it exists
  let sha = null;
  try {
    const getResp = await fetch(`${baseUrl}?ref=${branch}`, {
      headers: {
        "Authorization": `token ${token}`,
        "Accept": "application/vnd.github+json"
      }
    });
    if (getResp.ok) {
      const fileData = await getResp.json();
      sha = fileData.sha;
    }
  } catch (err) {
    // File doesn't exist, that's okay
  }
  
  const payload = {
    message,
    content: btoa(content),
    branch
  };
  
  if (sha) {
    payload.sha = sha;
  }
  
  const res = await fetch(baseUrl, {
    method: "PUT",
    headers: {
      "Authorization": `token ${token}`,
      "Content-Type": "application/json",
      "Accept": "application/vnd.github+json"
    },
    body: JSON.stringify(payload)
  });
  
  return await res.json();
}

// ============================================================================
// Authentication & Session Management
// ============================================================================

/**
 * DOM helper function
 */
function $(id) {
  return document.getElementById(id);
}

/**
 * Login handler
 * Encrypts and stores user passphrase in session storage
 */
async function handleLogin(buttonId = 'login_button', passphraseId = 'user_passphrase', overlayId = 'login_overlay') {
  const button = $(buttonId);
  const passphraseInput = $(passphraseId);
  const overlay = $(overlayId);
  
  if (!button || !passphraseInput) {
    console.error('Login elements not found');
    return;
  }
  
  button.onclick = async () => {
    const pass = passphraseInput.value.trim();
    if (!pass) {
      alert("Enter a passphrase.");
      return;
    }
    
    sessionStorage.setItem('infinity_pass', pass);
    
    if (overlay) {
      overlay.remove();
    }
    
    logDebug('User logged into Infinity system');
    
    // Emit custom event for other components
    window.dispatchEvent(new CustomEvent('infinity:login', { detail: { timestamp: Date.now() } }));
  };
}

/**
 * Debug logger
 */
function logDebug(message) {
  if (window.location.search.includes('debug=1')) {
    console.log(`[Infinity Debug] ${new Date().toISOString()} - ${message}`);
  }
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
  return !!sessionStorage.getItem('infinity_pass');
}

/**
 * Logout function
 */
function logout() {
  sessionStorage.removeItem('infinity_pass');
  sessionStorage.removeItem('github_token');
  window.dispatchEvent(new CustomEvent('infinity:logout'));
  logDebug('User logged out');
}

// ============================================================================
// Token & Wallet Management
// ============================================================================

/**
 * Token operations for Infinity wallet
 */
const TokenWallet = {
  /**
   * Get current token balance from local storage
   */
  getBalance() {
    const balance = localStorage.getItem('infinity_tokens');
    return balance ? parseInt(balance, 10) : 0;
  },
  
  /**
   * Set token balance
   */
  setBalance(amount) {
    localStorage.setItem('infinity_tokens', amount.toString());
    window.dispatchEvent(new CustomEvent('infinity:balance_changed', { 
      detail: { balance: amount } 
    }));
  },
  
  /**
   * Add tokens to balance
   */
  addTokens(amount) {
    const current = this.getBalance();
    this.setBalance(current + amount);
    return this.getBalance();
  },
  
  /**
   * Spend tokens if balance is sufficient
   */
  spendTokens(amount) {
    const current = this.getBalance();
    if (current >= amount) {
      this.setBalance(current - amount);
      return { success: true, newBalance: this.getBalance() };
    }
    return { success: false, error: 'Insufficient tokens' };
  },
  
  /**
   * Get transaction history
   */
  getHistory() {
    const history = localStorage.getItem('infinity_token_history');
    return history ? JSON.parse(history) : [];
  },
  
  /**
   * Add transaction to history
   */
  addTransaction(type, amount, description) {
    const history = this.getHistory();
    history.push({
      type,
      amount,
      description,
      timestamp: new Date().toISOString()
    });
    localStorage.setItem('infinity_token_history', JSON.stringify(history));
  }
};

// ============================================================================
// Exports (if using modules)
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    dualAIEncrypt,
    dualAIDecrypt,
    rogersRespond,
    commitToGitHub,
    handleLogin,
    isAuthenticated,
    logout,
    TokenWallet,
    getToken,
    setToken,
    logDebug
  };
}