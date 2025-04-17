// In your registration route
const bcrypt = require('bcrypt');
const saltRounds = 10;

app.post('/register', async (req, res) => {
  const { username, password } = req.body;

  try {
    const hash = await bcrypt.hash(password, saltRounds);

    // Save username and hash to your DB
    await db.query('INSERT INTO users (username, password_hash) VALUES (?, ?)', [username, hash]);

    res.status(200).json({ message: 'User registered' });
  } catch (err) {
    res.status(500).json({ message: 'Registration failed', error: err });
  }
});

// In main

app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    const result = await db.query('SELECT password_hash FROM users WHERE username = ?', [username]);

    if (result.length === 0) {
      return res.status(401).json({ message: 'Invalid username or password' });
    }

    const isMatch = await bcrypt.compare(password, result[0].password_hash);

    if (isMatch) {
      res.status(200).json({ message: 'Login successful' });
    } else {
      res.status(401).json({ message: 'Invalid username or password' });
    }
  } catch (err) {
    res.status(500).json({ message: 'Login failed', error: err });
  }
});
