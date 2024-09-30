import redis from 'redis';
export {readFromRedis, GetSearchParams};
const redisClient = redis.createClient({ url: "redis://localhost:6379" , database:1});
redisClient.on('error', err => console.log('Redis Client Error', err));

async function GetSearchParams() {
    try {
        const SearchParams = await redisClient.lPop('flights');
        if (SearchParams){
            console.log('Search Parameters:', SearchParams);
        }
    } catch (error) {console.error('Error getting search params', error);}
}


function readFromRedis() {
    redisClient.connect().then(() => {
        console.log('Connected to Redis');
    });
}
