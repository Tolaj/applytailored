/**
 * Authentication utility functions
 */

/**
 * Get the stored access token
 * @returns {string|null} The access token or null if not found
 */
function getAccessToken() {
    return localStorage.getItem('access_token');
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if token exists, false otherwise
 */
function isAuthenticated() {
    return getAccessToken() !== null;
}

/**
 * Redirect to login page if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/auth/login';
        return false;
    }
    return true;
}

/**
 * Make an authenticated fetch request
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise<Response>}
 */
async function fetchWithAuth(url, options = {}) {
    const token = getAccessToken();

    if (!token) {
        throw new Error('No access token found');
    }

    // Merge headers with Authorization header
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    // If unauthorized, redirect to login
    if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/auth/login';
        throw new Error('Unauthorized - redirecting to login');
    }

    return response;
}

/**
 * Logout user by removing token and redirecting
 */
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/auth/login';
}

/**
 * Make an authenticated API call and return JSON
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise<any>}
 */
async function apiCall(url, options = {}) {
    const response = await fetchWithAuth(url, options);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `Request failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * GET request with authentication
 * @param {string} url - The URL to fetch
 * @returns {Promise<any>}
 */
async function apiGet(url) {
    return apiCall(url, { method: 'GET' });
}

/**
 * POST request with authentication
 * @param {string} url - The URL to fetch
 * @param {object} data - Data to send in the request body
 * @returns {Promise<any>}
 */
async function apiPost(url, data) {
    return apiCall(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}

/**
 * PUT request with authentication
 * @param {string} url - The URL to fetch
 * @param {object} data - Data to send in the request body
 * @returns {Promise<any>}
 */
async function apiPut(url, data) {
    return apiCall(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}

/**
 * DELETE request with authentication
 * @param {string} url - The URL to fetch
 * @returns {Promise<any>}
 */
async function apiDelete(url) {
    return apiCall(url, { method: 'DELETE' });
}