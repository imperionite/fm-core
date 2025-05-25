# fm-core

Main backend API of FM system focusing on user management etc.


# connections

```sh
# Express/Mongo & Redis
const mongoUri = 'mongodb://myuser:mypassword@127.0.0.1:37017/mydatabase';

# redis or ioredis
const redis = require('redis');
const client = redis.createClient({
     url: 'redis://:devpassword@127.0.0.1:7379'
   });

client.connect()
.then(() => console.log('Connected to Redis'))
.catch(console.error);

```