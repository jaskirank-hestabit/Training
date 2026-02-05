const http = require('http');

let count = 0;

const server = http.createServer((req, res) => {
    if(req.url === '/ping') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({timestamp: new Date().toISOString() }));
    }
    
    else if(req.url === '/headers'){
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(req.headers, null, 2));
    }

    else if(req.url === '/count'){
        count++;
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({count: count}));
    }

    else{
        res.writeHead(404);
        res.end('Not Found');
    }
});

server.listen(3000, ()=>{
    console.log('Server running on http://localhost:3000');
})