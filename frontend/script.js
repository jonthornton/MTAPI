const API_BASE_URL = '/api/mta';

class SubwayMapApp {
    constructor() {
        this.allTrainData = [];
        this.lastUpdated = null;
        this.mapInstance = null;
        this.isFetching = false;
        this.init();
    }

    async init() {
        this.mapInstance = initLeafletMap('map');
        this.setupEventListeners();
        await this.fetchData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        document.getElementById('refresh-btn').addEventListener('click', () => {
            if (!this.isFetching) {
                 this.fetchData();
            }
        });
    }

    async fetchData() {
        if (this.isFetching) return;
        this.isFetching = true;
        
        const refreshBtn = document.getElementById('refresh-btn');
        const loadingMessageEl = document.getElementById('loading-message');
        const lastUpdatedEl = document.getElementById('last-updated');
        
        refreshBtn.disabled = true;
        refreshBtn.textContent = 'Refreshing...';
        loadingMessageEl.textContent = 'Fetching latest train data...';
        loadingMessageEl.style.display = 'block';
        document.getElementById('train-list').innerHTML = '';

        try {
            const response = await fetch(`${API_BASE_URL}/feeds/all`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Failed to fetch data: ${response.status} ${errorData.error || ''}`);
            }
            const rawData = await response.json();
            
            this.allTrainData = rawData
                .filter(feed => feed.data && !feed.error)
                .flatMap(feed => feed.data);

            this.lastUpdated = new Date();
            this.updateUI();
            if (window.updateMapWithTrainLocations) {
                window.updateMapWithTrainLocations(this.allTrainData, this.getLineColor.bind(this));
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            lastUpdatedEl.textContent = `Error: ${error.message}`;
            loadingMessageEl.textContent = `Failed to load train data. ${error.message}`;
        } finally {
            this.isFetching = false;
            refreshBtn.disabled = false;
            refreshBtn.textContent = 'Refresh Data';
            if (this.allTrainData.length > 0) {
                loadingMessageEl.style.display = 'none';
            }
        }
    }

    updateUI() {
        const lastUpdatedEl = document.getElementById('last-updated');
        if (this.lastUpdated) {
            lastUpdatedEl.textContent = `Last updated: ${this.lastUpdated.toLocaleTimeString()}`;
        }
        this.updateTrainList();
    }

    updateTrainList() {
        const trainListEl = document.getElementById('train-list');
        const loadingMessageEl = document.getElementById('loading-message');
        trainListEl.innerHTML = '';
        
        if (this.allTrainData.length === 0 && !this.isFetching) {
             if (!loadingMessageEl.textContent.startsWith("Failed")) {
                loadingMessageEl.textContent = 'No active train data found or all feeds failed.';
             }
             loadingMessageEl.style.display = 'block';
             return;
        } else if (this.allTrainData.length > 0) {
            loadingMessageEl.style.display = 'none';
        }

        const trainsByRoute = {};
        this.allTrainData.forEach(train => {
            if (!trainsByRoute[train.routeId]) {
                trainsByRoute[train.routeId] = [];
            }
            trainsByRoute[train.routeId].push(train);
        });
        
        Object.entries(trainsByRoute).sort(([routeA], [routeB]) => routeA.localeCompare(routeB)).forEach(([routeId, trains]) => {
            if (!routeId) return;
            const routeEl = document.createElement('div');
            routeEl.className = 'train-item';
            routeEl.style.borderLeftColor = this.getLineColor(routeId);
            
            const sanitizedRouteId = routeId.replace(/[^a-zA-Z0-9]/g, '');

            routeEl.innerHTML = `
                <span class="train-line-icon line-${sanitizedRouteId}">${routeId}</span>
                <div class="train-details">
                    <strong>Route ${routeId}</strong>
                    <p>${trains.length} trip update(s)</p>
                </div>
            `;
            trainListEl.appendChild(routeEl);
        });
    }

    getLineColor(line) {
        const route = line.toUpperCase();
        const colors = {
            '1': '#EE352E', '2': '#EE352E', '3': '#EE352E',
            '4': '#00933C', '5': '#00933C', '6': '#00933C',
            '7': '#B933AD',
            'A': '#0039A6', 'C': '#0039A6', 'E': '#0039A6',
            'B': '#FF6319', 'D': '#FF6319', 'F': '#FF6319', 'M': '#FF6319',
            'G': '#6CBE45',
            'J': '#996633', 'Z': '#996633',
            'L': '#A7A9AC',
            'N': '#FCCC0A', 'Q': '#FCCC0A', 'R': '#FCCC0A', 'W': '#FCCC0A',
            'S': '#808183', 'GS': '#808183', 'FS':'#808183', 'H':'#808183',
            'SI': '#0039A6',
        };
        return colors[route] || '#555555';
    }

    startAutoRefresh() {
        setInterval(() => {
            if (!this.isFetching) {
                 this.fetchData();
            }
        }, 30000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SubwayMapApp();
});