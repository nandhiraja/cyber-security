const express = require('express');
const app = express();
const PORT = 3000;

// Middleware to parse JSON request bodies
app.use(express.json());

// In-memory "database" 
let users = [
    { id: 1, name: "Alice Smith", email: "alice@example.com" },
    { id: 2, name: "Bob Jones", email: "bob@example.com" }
];

app.post('/api/users', (req, res) => {
    const { name, email } = req.body;

    const newUser = {
        id: users.length > 0 ? users[users.length - 1].id + 1 : 1,
        name,
        email
    };

    users.push(newUser);
    res.status(201).json(newUser);
});

// -------------------------------------------------------------------
// 2. READ All - GET /api/users
//    READ One - GET /api/users/:id
// -------------------------------------------------------------------
app.get('/api/users', (req, res) => {
    res.status(200).json(users);
});

app.get('/api/users/:id', (req, res) => {
    const userId = parseInt(req.params.id);
    const user = users.find(u => u.id === userId);

    if (!user) {
        return res.status(404).json({ message: "User not found." });
    }

    res.status(200).json(user);
});

// -------------------------------------------------------------------
// 3. UPDATE - PUT /api/users/:id
// -------------------------------------------------------------------
app.put('/api/users/:id', (req, res) => {
    const userId = parseInt(req.params.id);
    const userIndex = users.findIndex(u => u.id === userId);

    if (userIndex === -1) {
        return res.status(404).json({ message: "User not found." });
    }

    const { name, email } = req.body;

    if (name) users[userIndex].name = name;
    if (email) users[userIndex].email = email;

    res.status(200).json(users[userIndex]);
});

// -------------------------------------------------------------------
// 4. DELETE - DELETE /api/users/:id
// -------------------------------------------------------------------
app.delete('/api/users/:id', (req, res) => {
    const userId = parseInt(req.params.id);
    const userIndex = users.findIndex(u => u.id === userId);

    if (userIndex === -1) {
        return res.status(404).json({ message: "User not found." });
    }

    const deletedUser = users.splice(userIndex, 1);
    
    res.status(200).json({ message: "User deleted successfully.", user: deletedUser[0] });
});


app.listen(PORT, () => {
    console.log(`Server running smoothly on http://localhost:${PORT}`);
});