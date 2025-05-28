const express = require('express');
const fetch = require('node-fetch');
const GtfsRealtimeBindings = require('gtfs-realtime-bindings');
const router = express.Router();

// MTA Feed URLs - No API key required!
const MTA_FEEDS = {
  '1234567': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
  'ace': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace',
  'bdfm': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm',
  'g': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g',
  'jz': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz',
  'l': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',
  'nqrw': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw',
  'si': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si'
};

// Add CORS headers to all MTA API responses
router.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

// Get real-time data for a specific feed
router.get('/feed/:feedId', async (req, res) => {
  try {
    const feedId = req.params.feedId;
    const feedUrl = MTA_FEEDS[feedId];
    
    if (!feedUrl) {
      return res.status(404).json({ error: 'Feed not found' });
    }

    console.log(`Fetching feed ${feedId} from ${feedUrl}`);
    
    const response = await fetch(feedUrl, {
      headers: {
        'User-Agent': 'SubwayMap/1.0',
        'Accept': 'application/x-protobuf'
      },
      timeout: 10000 // 10 second timeout
    });

    if (!response.ok) {
      console.error(`HTTP error for feed ${feedId}: ${response.status} ${response.statusText}`);
      throw new Error(`HTTP error! status: ${response.status} ${response.statusText}`);
    }

    const buffer = await response.buffer();
    console.log(`Received ${buffer.length} bytes for feed ${feedId}`);
    
    const feed = GtfsRealtimeBindings.transit_realtime.FeedMessage.decode(buffer);
    const processedData = processFeedData(feed);
    
    console.log(`Processed ${processedData.length} train updates for feed ${feedId}`);
    res.json(processedData);
  } catch (error) {
    console.error(`Error fetching MTA feed ${req.params.feedId}:`, error.message);
    res.status(500).json({ 
      error: 'Failed to fetch feed data', 
      details: error.message,
      feedId: req.params.feedId,
      timestamp: new Date().toISOString()
    });
  }
});

// Get all feeds with better error handling
router.get('/feeds/all', async (req, res) => {
  try {
    console.log('Starting to fetch all MTA feeds...');
    
    const allFeedsData = await Promise.allSettled(
      Object.entries(MTA_FEEDS).map(async ([feedId, feedUrl]) => {
        try {
          console.log(`Fetching feed ${feedId}...`);
          
          const response = await fetch(feedUrl, {
            headers: {
              'User-Agent': 'SubwayMap/1.0',
              'Accept': 'application/x-protobuf'
            },
            timeout: 10000
          });
          
          if (!response.ok) {
            console.error(`Error fetching feed ${feedId}: ${response.status} ${response.statusText}`);
            return { feedId, error: true, status: response.status, statusText: response.statusText };
          }
          
          const buffer = await response.buffer();
          const feed = GtfsRealtimeBindings.transit_realtime.FeedMessage.decode(buffer);
          const processedData = processFeedData(feed);
          
          console.log(`Successfully processed feed ${feedId}: ${processedData.length} updates`);
          
          return {
            feedId,
            data: processedData,
            timestamp: new Date().toISOString(),
            count: processedData.length
          };
        } catch (error) {
          console.error(`Error processing feed ${feedId}:`, error.message);
          return { feedId, error: true, details: error.message };
        }
      })
    );
    
    // Process results from Promise.allSettled
    const successfulFeeds = allFeedsData
      .filter(result => result.status === 'fulfilled' && result.value && !result.value.error)
      .map(result => result.value);
    
    const failedFeeds = allFeedsData
      .filter(result => result.status === 'rejected' || (result.status === 'fulfilled' && result.value && result.value.error))
      .map(result => result.status === 'rejected' ? { error: result.reason.message } : result.value);
    
    console.log(`Feeds summary: ${successfulFeeds.length} successful, ${failedFeeds.length} failed`);
    
    res.json({
      feeds: successfulFeeds,
      totalTrains: successfulFeeds.reduce((sum, feed) => sum + (feed.count || 0), 0),
      errors: failedFeeds.length > 0 ? failedFeeds : undefined,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error fetching all feeds:', error.message);
    res.status(500).json({ 
      error: 'Failed to fetch feeds', 
      details: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Test endpoint to check MTA connectivity
router.get('/test', async (req, res) => {
  try {
    const testFeed = MTA_FEEDS['ace']; // Test with A/C/E feed
    console.log(`Testing MTA connectivity with: ${testFeed}`);
    
    const response = await fetch(testFeed, {
      headers: {
        'User-Agent': 'SubwayMap/1.0',
        'Accept': 'application/x-protobuf'
      },
      timeout: 5000
    });
    
    const buffer = await response.buffer();
    const feed = GtfsRealtimeBindings.transit_realtime.FeedMessage.decode(buffer);
    
    res.json({
      status: 'success',
      responseStatus: response.status,
      bufferSize: buffer.length,
      entityCount: feed.entity ? feed.entity.length : 0,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

function processFeedData(feed) {
  const trains = [];
  
  if (!feed || !feed.entity) {
    console.warn('No entities found in feed');
    return trains;
  }
  
  feed.entity.forEach((entity, index) => {
    try {
      if (entity.tripUpdate && entity.tripUpdate.trip && entity.tripUpdate.stopTimeUpdate) {
        const tripUpdate = entity.tripUpdate;
        const routeId = tripUpdate.trip.routeId;
        
        if (!routeId) {
          return; // Skip if no route ID
        }
        
        tripUpdate.stopTimeUpdate.forEach(stopUpdate => {
          try {
            const arrivalTime = stopUpdate.arrival && stopUpdate.arrival.time ? Number(stopUpdate.arrival.time) : null;
            const departureTime = stopUpdate.departure && stopUpdate.departure.time ? Number(stopUpdate.departure.time) : null;

            if ((arrivalTime || departureTime) && stopUpdate.stopId) {
              trains.push({
                tripId: tripUpdate.trip.tripId || `unknown_${index}`,
                routeId: routeId,
                stopId: stopUpdate.stopId,
                arrival: arrivalTime ? new Date(arrivalTime * 1000) : null,
                departure: departureTime ? new Date(departureTime * 1000) : null,
                delay: (stopUpdate.arrival && stopUpdate.arrival.delay) ? stopUpdate.arrival.delay : 
                       (stopUpdate.departure && stopUpdate.departure.delay) ? stopUpdate.departure.delay : 0
              });
            }
          } catch (stopError) {
            console.warn(`Error processing stop update:`, stopError.message);
          }
        });
      }
    } catch (entityError) {
      console.warn(`Error processing entity ${index}:`, entityError.message);
    }
  });
  
  return trains;
}

module.exports = router;