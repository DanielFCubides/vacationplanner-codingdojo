import redis from 'redis';

export {readFromRedis, GetSearchParams, GetSearchParams2};
const redisClient = redis.createClient({url: "redis://redis-cache:6379", database: 1});
redisClient.on('error', err => console.log('Redis Client Error', err));

async function GetSearchParams() {
    try {
        const SearchParams = await redisClient.lPop('search_params');
        if (SearchParams) {
            console.log('Search Parameters:', SearchParams);
        }
    } catch (error) {
        console.error('Error getting search params', error);
    }
}


function readFromRedis() {
    redisClient.connect().then(() => {
        console.log('Connected to Redis');
    });
}

async function GetSearchParams2() {
    try {
        await redisClient.subscribe('search_params', (msg) => {
            console.log('Subscribed to search_params', msg);
        });
    } catch (error) {
        console.error('Error getting search params', error);
    }

}