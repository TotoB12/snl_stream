const express = require('express');
const path = require('path');
const app = express();
const port = 3000;

app.use(express.static('.'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + '/index.html'));
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});