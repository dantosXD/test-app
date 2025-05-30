# Airtable Clone Frontend

This directory contains the frontend for the Airtable clone application, built with React and Vite.

## Setup and Running

### Prerequisites

*   Node.js (version 18.x or higher recommended, as per React/Vite typical requirements. Note: The environment this was developed in showed Node v18.19.1, but some newer dependencies like `react-router-dom@7+` might ideally want Node 20+).
*   npm or yarn

### 1. Install Dependencies

Navigate to this `frontend` directory in your terminal.

If you are using npm:
```bash
npm install
```

If you are using yarn:
```bash
yarn install
```

### 2. Environment Variables

This frontend application connects to a backend API. The API base URL is configured in `src/services/api.js`. By default, it is set to `http://localhost:8000`.

Ensure your backend server is running and accessible at this address. If your backend runs on a different port or URL, you will need to update the `baseURL` in `src/services/api.js`.

No specific `.env` file is required for this frontend for basic operation, unless you plan to add environment-specific configurations (e.g., for different API URLs in development vs. production through Vite's env handling).

### 3. Run the Development Server

Once dependencies are installed, you can start the development server.

If you are using npm:
```bash
npm run dev
```

If you are using yarn:
```bash
yarn dev
```

This will typically start the development server on `http://localhost:5173` (Vite's default) or another port if 5173 is busy. Open your browser and navigate to the provided URL to see the application.

### Backend Expectation

This frontend expects the backend API to be running on `http://localhost:8000`. Make sure your [backend server](../backend/README.md) is set up and running before you start the frontend application. The backend does not use an `/api/v1` prefix for its routes (e.g., endpoints are `/auth/login`, `/bases`).

---

This setup provides a React frontend with basic authentication flow (login, register), a dashboard to display bases, and routing. It uses Zustand for state management and Axios for API calls.
