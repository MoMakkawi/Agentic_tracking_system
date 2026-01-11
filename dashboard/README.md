# Agentic Tracking System - Dashboard

## Index

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Locally](#running-locally)
  - [Building for Production](#building-for-production)
- [Project Structure](#project-structure)
- [Styling Architecture](#styling-architecture)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **Agentic Tracking System Dashboard** is a modern, high-performance web application designed to monitor and manage agentic workflows, attendance, and system alerts. Built with **React** and **Vite**, it features a responsive, glassmorphism-inspired UI ("Deep Ocean / Obsidian Theme") that provides real-time insights and control over the tracking system.

---

## Key Features

-   **Real-time Overview**: Comprehensive dashboard displaying key metrics and system health at a glance.
-   **Attendance Tracking**: Detailed logs and management interfaces for monitoring attendance records.
-   **Group Management**: Tools to organize and manage user groups effectively.
-   **Alerts System**: Real-time notification system for critical events and system anomalies.
-   **Agent Interface**: Direct interaction capabilities with the system's orchestrated agents.
-   **Premium UI**: A custom-designed, dark-themed interface featuring glassmorphism effects and smooth animations.

---

## Tech Stack

-   **Core**: [React 18](https://react.dev/), [Vite](https://vitejs.dev/)
-   **Routing**: [React Router DOM v6](https://reactrouter.com/)
-   **Styling**: Vanilla CSS3 (Custom Variables, Flexbox/Grid)
-   **HTTP Client**: [Axios](https://axios-http.com/)
-   **Icons**: [Lucide React](https://lucide.dev/)
-   **Notifications**: [React Hot Toast](https://react-hot-toast.com/)

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your local development machine:

-   **Node.js**: v18.0.0 or higher
-   **npm**: v9.0.0 or higher

### Installation

1.  Navigate to the dashboard directory:
    ```bash
    cd dashboard
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

### Running Locally

Start the development server with hot-reload:

```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or the next available port).

### Building for Production

To create an optimized production build:

```bash
npm run build
```

You can preview the production build locally using:

```bash
npm run preview
```
---

## Project Structure

```bash
dashboard/
├── public/              # Static assets (favicons, manifests)
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Common/      # Atomic components (Buttons, Cards, Inputs)
│   │   └── Layout/      # Structural components (Sidebar, Headers)
│   ├── pages/           # Main application views/routes
│   │   ├── Overview/    # Dashboard home
│   │   ├── Attendance/  # Attendance logs
│   │   ├── Groups/      # Group management
│   │   ├── Alerts/      # System notifications
│   │   └── Agent/       # Agent chat interface
│   ├── services/        # API integration and service logic
│   ├── utils/           # Helper functions and constants
│   ├── App.jsx          # Main application component
│   ├── main.jsx         # Application entry point
│   └── index.css        # Global styles and theme variables
├── package.json         # Dependencies and scripts
└── vite.config.js       # Vite configuration
```

---

## Styling Architecture

The project uses a native CSS variable system for theming, located in `src/index.css`. This includes:

-   **Colors**: Semantic naming for backgrounds (`--bg-primary`, `--bg-secondary`) and accents (`--accent-primary`, `--accent-success`).
-   **Glassmorphism**: Utility classes (`.glass`, `.glass-tabs`) for the signature frosted glass look.
-   **Typography**: Using 'Inter' for UI text and 'Outfit' for headings.
-   **Animations**: Keyframes for smooth entry (`fadeIn`) and transitions (`--transition-base`).

---

## Contributing

1.  Ensure your code follows the existing style guidelines.
2.  Run `npm run lint` before committing to catch any static analysis errors.
3.  Keep components modular and reusable.

---

## License

See LICENSE in project root