const express = require('express');
const path = require('path');
const fs = require('fs').promises;
const fsSync = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// In-memory storage for tokens and users (in production, use a database)
// NOTE: Rate limiting should be added for production use to prevent abuse
let users = {};
let tokenWallets = {};

// Login endpoint
app.post('/api/login', async (req, res) => {
    const { username, password } = req.body;
    
    // Simple authentication (in production, use proper password hashing)
    if (!users[username]) {
        users[username] = { password, tokens: 0 };
        tokenWallets[username] = [];
    } else if (users[username].password !== password) {
        return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
    
    // Create a simple token
    const token = Buffer.from(`${username}:${Date.now()}`).toString('base64');
    
    // Save login as server-side commit
    const commitLog = {
        timestamp: new Date().toISOString(),
        username: username,
        action: 'login',
        token: token
    };
    
    // Append to commit log file (async)
    const logEntry = JSON.stringify(commitLog) + '\n';
    try {
        await fs.appendFile(path.join(__dirname, 'commit-log.txt'), logEntry);
    } catch (error) {
        console.error('Error writing to commit log:', error);
    }
    
    res.json({ 
        success: true, 
        token: token,
        username: username,
        tokens: users[username].tokens
    });
});

// Token wallet endpoints
app.get('/api/wallet/:username', (req, res) => {
    const { username } = req.params;
    
    if (!tokenWallets[username]) {
        tokenWallets[username] = [];
    }
    
    res.json({ 
        success: true,
        tokens: tokenWallets[username],
        balance: users[username]?.tokens || 0
    });
});

app.post('/api/wallet/add', async (req, res) => {
    const { username, tokenType, amount } = req.body;
    
    if (!tokenWallets[username]) {
        tokenWallets[username] = [];
    }
    
    const newToken = {
        id: Date.now(),
        type: tokenType,
        amount: amount,
        timestamp: new Date().toISOString()
    };
    
    tokenWallets[username].push(newToken);
    
    if (!users[username]) {
        users[username] = { tokens: 0 };
    }
    users[username].tokens += parseInt(amount);
    
    // Log the token addition as a commit (async)
    const commitLog = {
        timestamp: new Date().toISOString(),
        username: username,
        action: 'add_token',
        tokenType: tokenType,
        amount: amount
    };
    
    try {
        await fs.appendFile(path.join(__dirname, 'commit-log.txt'), JSON.stringify(commitLog) + '\n');
    } catch (error) {
        console.error('Error writing to commit log:', error);
    }
    
    res.json({ 
        success: true,
        wallet: tokenWallets[username],
        balance: users[username].tokens
    });
});

// Get commit log
app.get('/api/commits', async (req, res) => {
    try {
        const logPath = path.join(__dirname, 'commit-log.txt');
        
        // Check if file exists synchronously (small operation)
        if (!fsSync.existsSync(logPath)) {
            return res.json({ success: true, commits: [] });
        }
        
        const logContent = await fs.readFile(logPath, 'utf8');
        const commits = logContent
            .split('\n')
            .filter(line => line.trim())
            .map(line => JSON.parse(line));
        
        res.json({ success: true, commits: commits });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
