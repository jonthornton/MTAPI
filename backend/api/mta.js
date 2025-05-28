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

// Get real-time data for a specific feed
router.get('/feed/:feedId', async (req, res) => {
  try {
    const feedId = req.params.feedId;
    const feedUrl = MTA_FEEDS[feedId];
    
    if (!feedUrl) {
      return res.status(404).json({ error: 'Feed not found' });
    }

    const response = await fetch(feedUrl);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const buffer = await response.buffer();
    const feed = GtfsRealtimeBindings.transit_realtime.FeedMessage.decode(buffer);
    
    const processedData = processFeedData(feed);
    res.json(processedData);
  } catch (error) {
    console.error('Error fetching MTA feed:', error.message);
    res.status(500).json({ error: 'Failed to fetch feed data', details: error.message });
  }
});

// Get all feeds
router.get('/feeds/all', async (req, res) => {
  try {
    const allFeedsData = await Promise.all(
      Object.entries(MTA_FEEDS).map(async ([feedId, feedUrl]) => {
        try {
          const response = await fetch(feedUrl);
          
          if (!response.ok) {
             console.error(`Error fetching feed ${feedId}: ${response.status}`);
             return { feedId, error: true, status: response.status };
          }
          
          const buffer = await response.buffer();
          const feed = GtfsRealtimeBindings.transit_realtime.FeedMessage.decode(buffer);
          
          return {
            feedId,
            data: processFeedData(feed)
          };
        } catch (error) {
          console.error(`Error processing feed ${feedId}:`, error.message);
          return { feedId, error: true, details: error.message };
        }
      })
    );
    
    res.json(allFeedsData.filter(f => !f.error));
  } catch (error) {
    console.error('Error fetching all feeds:', error.message);
    res.status(500).json({ error: 'Failed to fetch feeds', details: error.message });
  }
});

function processFeedData(feed) {
  const trains = [];
  feed.entity.forEach(entity => {
    if (entity.tripUpdate) {
      const tripUpdate = entity.tripUpdate;
      const routeId = tripUpdate.trip.routeId;
      
      tripUpdate.stopTimeUpdate.forEach(stopUpdate => {
        const arrivalTime = stopUpdate.arrival && stopUpdate.arrival.time ? Number(stopUpdate.arrival.time) : null;
        const departureTime = stopUpdate.departure && stopUpdate.departure.time ? Number(stopUpdate.departure.time) : null;

        if (arrivalTime || departureTime) {
          trains.push({
            tripId: tripUpdate.trip.tripId,
            routeId: routeId,
            stopId: stopUpdate.stopId,
            arrival: arrivalTime ? new Date(arrivalTime * 1000) : null,
            departure: departureTime ? new Date(departureTime * 1000) : null,
            delay: stopUpdate.arrival && stopUpdate.arrival.delay ? stopUpdate.arrival.delay : (stopUpdate.departure && stopUpdate.departure.delay ? stopUpdate.departure.delay : 0)
          });
        }
      });
    }
  });
  return trains;
}

module.exports = router;