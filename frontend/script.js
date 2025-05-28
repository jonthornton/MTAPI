const API_BASE_URL = '/api/mta';

class SubwayMapApp {
    constructor() {
        this.allTrainData = [];
        this.lastUpdated = null;
        this.mapInstance = null;
        this.isFetching = false;
        this.errorCount = 0;
        this.maxErrors = 3;
        this.init();
    }

    async init() {
        this.mapInstance = initLeafletMap('map');
        this.setupEventListeners();
        
        // Test API connectivity first
        await this.testAPI();
        
        // Then fetch data
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

    async testAPI() {
        try {
            console.log('Testing API connectivity...');
            const response = await fetch(`${API_BASE_URL}/test`);
            const result = await response.json();
            console.log('API test result:', result);
            
            if (result.status === 'success') {
                console.log('✅ API connectivity confirmed');
            } else {
                console.warn('⚠️ API test failed:', result);
            }
        } catch (error) {
            console.error('❌ API test error:', error);
        }
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
            console.log('Fetching train data...');
            const response = await fetch(`${API_BASE_URL}/feeds/all`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Received data:', data);
            
            if (data.feeds && Array.isArray(data.feeds)) {
                this.allTrainData = data.feeds.flatMap(feed => feed.data || []);
                console.log(`Processed ${this.allTrainData.length} total train updates`);
            } else {
                console.warn('Unexpected data format:', data);
                this.allTrainData = [];
            }

            this.lastUpdated = new Date();
            this.errorCount = 0; // Reset error count on success
            this.updateUI();
            
            if (window.updateMapWithTrainLocations) {
                window.updateMapWithTrainLocations(this.allTrainData, this.getLineColor.bind(this));
            }
            
        } catch (error) {
            console.error('Error fetching data:', error);
            this.errorCount++;
            
            let errorMessage = 'Failed to load train data.';
            
            if (error.message.includes('CORS')) {
                errorMessage = 'CORS error: Try refreshing the page or check your connection.';
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Network error: Check your internet connection.';
            } else if (error.message.includes('HTTP 5')) {
                errorMessage = 'Server error: The MTA service may be temporarily unavailable.';
            } else {
                errorMessage = `Error: ${error.message}`;
            }
            
            lastUpdatedEl.textContent = errorMessage;
            loadingMessageEl.textContent = errorMessage;
            
            // Show retry message if multiple errors
            if (this.errorCount >= this.maxErrors) {
                loadingMessageEl.textContent += ' Will retry automatically in 60 seconds.';
            }
            
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
             if (!loadingMessageEl.textContent.includes('Error') && !loadingMessageEl.textContent.includes('Failed')) {
                loadingMessageEl.textContent = 'No active train data available. The MTA feeds may be temporarily unavailable.';
             }
             loadingMessageEl.style.display = 'block';
             return;
        } else if (this.allTrainData.length > 0) {
            loadingMessageEl.style.display = 'none';
        }

        const trainsByRoute = {};
        this.allTrainData.forEach(train => {
            if (train.routeId && !trainsByRoute[train.routeId]) {
                trainsByRoute[train.routeId] = [];
            }
            if (train.routeId) {
                trainsByRoute[train.routeId].push(train);
            }
        });
        
        const sortedRoutes = Object.entries(trainsByRoute).sort(([routeA], [routeB]) => {
            // Custom sort: numbers first, then letters
            const aIsNumber = /^\d/.test(routeA);
            const bIsNumber = /^\d/.test(routeB);
            
            if (aIsNumber && !bIsNumber) return -1;
            if (!aIsNumber && bIsNumber) return 1;
            
            return routeA.localeCompare(routeB);
        });
        
        sortedRoutes.forEach(([routeId, trains]) => {
            const routeEl = document.createElement('div');
            routeEl.className = 'train-item';
            routeEl.style.borderLeftColor = this.getLineColor(routeId);
            
            const sanitizedRouteId = routeId.replace(/[^a-zA-Z0-9]/g, '');

            routeEl.innerHTML = `
                <span class="train-line-icon line-${sanitizedRouteId}">${routeId}</span>
                <div class="train-details">
                    <strong>Route ${routeId}</strong>
                    <p>${trains.length} active train(s)</p>
                </div>
            `;
            trainListEl.appendChild(routeEl);
        });
        
        // Add summary info
        const summaryEl = document.createElement('div');
        summaryEl.className = 'summary-info';
        summaryEl.innerHTML = `
            <div style="margin-top: 1rem; padding: 0.5rem; background: #f0f8ff; border-radius: 4px; font-size: 0.9rem; color: #666;">
                <strong>Total:</strong> ${Object.keys(trainsByRoute).length} routes, ${this.allTrainData.length} trains
            </div>
        `;
        trainListEl.appendChild(summaryEl);
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
                console.log('Auto-refreshing data...');
                this.fetchData();
            }
        }, 30000); // Refresh every 30 seconds
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚇 NYC Subway Map starting...');
    new SubwayMapApp();
});