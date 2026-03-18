# Fair Hiring Network - Frontend

**React-powered dashboard for AI-driven recruitment with Auth0 authentication**

---

## Overview

The FHN frontend is a premium React application providing comprehensive dashboards for candidates and companies. It features immersive 3D experiences, smooth animations, and real-time AI integration with Google Gemini and ElevenLabs.

### Key Capabilities

- **Multi-Role Experience** - Separate flows for Candidates, Companies, and Reviewers
- **AI-Powered Interviews** - Real-time video interviews with Google Gemini AI
- **Skill Passports** - Cryptographically verified credentials visualization
- **Interactive Dashboards** - Real-time analytics with Recharts
- **3D Experiences** - Immersive Three.js landing page
- **Smooth Interactions** - Framer Motion + GSAP animations with Lenis scroll

---

## Architecture

### Frontend Architecture (ASCII)

```
+-----------------------------------------------------------------------------+
|                              FRONTEND SERVICE LAYER                          |
+-----------------------------------------------------------------------------+
|                                                                             |
|  +----------------------------------------------------------------------+   |
|  |                          BROWSER (Vite Dev Server)                  |   |
|  |  ┌────────────────────────────────────────────────────────────────┐ |   |
|  |  |                     React Application (Root)                   │ |   |
|  |  │  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │ |   |
|  |  │  │  BrowserRouter  │  │   Auth0Provider │  │   Lenis Scroll │  │ |   |
|  |  │  │  Route Manager  │  │   Authentication│  │  Smooth Scroll│  │ |   |
|  |  │  └─────────────────┘  └─────────────────┘  └────────────────┘  │ |   |
|  |  └────────────────────────────────────────────────────────────────┘ |   |
|  └───────────────────────────────────────────────────────────────────────┘   |
|                                        │                                      |
|  +--------------------------------------+------------------------------------+  |
|  │                                      ▼                                    |  |
|  |  +----------------------------------------------------------------------+ |  |
|  |  |                          PAGES LAYER                                | |  |
|  |  │  +-------------+  +-------------+  +-------------+  +------------+ | |  |
|  |  │  │   Landing   │  │   Company   │  │  Candidate  │  │  Interview │ | |  |
|  |  │  │    Page     │  │  Dashboard  │  │  Experience │  │   Protocall│ | |  |
|  |  │  │  (Hero, 3D) │  │  (Jobs, Pipelines) │ (Applications)│(AI Session)│ | |  |
|  |  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ | |  |
|  │  └──────────────────────────────────────────────────────────────────────┘ |  |
|  +----------------------------------------------------------------------------+  |
|                                        │                                       |
|  +--------------------------------------+------------------------------------+  |
|  │                                      ▼                                    |  |
|  |  +----------------------------------------------------------------------+ |  |
|  |  |                      COMPONENTS LAYER                               | |  |
|  |  │  +--------+ +--------+ +--------+ +--------+ +--------+ +--------+  | |  |
|  |  │  │ Navbar │ │ Grid+  │ │ JobCard│ │Candidate│ │ Skill  │ │ Interview│ | |  |
|  |  │  │Menu    │ │ Modal  │ │Company │ │  Card   │ │ Passport│ │  Setup   │ | |  |
|  |  │  │        │ │        │ │  Card  │ │        │ │ Viewer │ │ Session  │ | |  |
|  |  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘  | |  |
|  │  └──────────────────────────────────────────────────────────────────────┘ |  |
|  +----------------------------------------------------------------------------+  |
|                                        │                                       |
|  +--------------------------------------+------------------------------------+  |
|  │                                      ▼                                    |  |
|  |  +----------------------------------------------------------------------+ |  |
|  |  |                         SERVICES LAYER                              | |  |
|  |  │  +------------------------+  +---------------------------+          | |  |
|  |  │  │      API Client        │  │    Auth Integration      │          | |  |
|  |  │  │      (Axios + JWT)     │  │    (Auth0 SDK + Hooks)   │          | |  |
|  |  │  └────────────────────────┘  └───────────────────────────┘          | |  |
|  │  │  +------------------------+  +---------------------------+          | |  |
|  |  │  │    AI Services        │  │     Audio Utilities      │          | |  |
|  │  │  │ (Gemini + ElevenLabs) │  │   (MediaRecorder, etc)   │          | |  |
|  |  │  └────────────────────────┘  └───────────────────────────┘          | |  |
|  │  └──────────────────────────────────────────────────────────────────────┘ |  |
|  +----------------------------------------------------------------------------+  |
|                                        │                                       |
|                                        ▼                                       |
|                         +-------------------+                                  |
|                         |   External APIs  |                                  |
|                         +-------------------+                                  |
|                         |  • Auth0 (Auth)  |                                  |
|                         |  • Backend API  |                                  │
|                         |  • Gemini 2.0   |                                  |
|                         |  • ElevenLabs   |                                  |
|                         +-------------------+                                  |
+-------------------------------------------------------------------------------+
```

### Directory Structure

```
fair-hiring-frontend/
├── src/
│   ├── api/
│   │   ├── backend.js          # Axios instance with JWT interceptor
│   │   └── index.js            # API wrapper functions
│   │
│   ├── auth/
│   │   ├── auth0.js            # Auth0 configuration
│   │   └── useAuth.js          # Custom auth hook
│   │
│   ├── components/
│   │   ├── common/             # Shared components
│   │   │   ├── Navbar.jsx      # Navigation bar
│   │   │   ├── MenuOverlay.jsx # Mobile menu
│   │   │   ├── GridPlus.jsx    # Custom grid layout
│   │   │   └── JobDetailsModal.jsx
│   │   │
│   │   ├── company/            # Company-specific components
│   │   │   ├── CompanyAuth.jsx
│   │   │   ├── CompanyDashboard.jsx
│   │   │   ├── CompanyHiringFlow.jsx
│   │   │   ├── CompanyRolePipeline.jsx
│   │   │   ├── CompanyCandidateReview.jsx
│   │   │   └── CompanySelectedCandidates.jsx
│   │   │
│   │   ├── candidate/          # Candidate-specific components
│   │   │   ├── CandidateAuth.jsx
│   │   │   ├── CandidateExperience.jsx
│   │   │   ├── CandidateApply.jsx
│   │   │   └── SkillPassport.jsx
│   │   │
│   │   ├── protocall/          # AI Interview system
│   │   │   ├── ProtocallApp.jsx
│   │   │   ├── InterviewSetup.jsx
│   │   │   ├── InterviewSession.jsx
│   │   │   ├── AnalysisReport.jsx
│   │   │   ├── audioUtils.js
│   │   │   ├── analysisService.js
│   │   │   └── elevenlabsService.js
│   │   │
│   │   ├── landing/            # Landing page components
│   │   │   ├── Hero.jsx
│   │   │   ├── ParallaxObject.jsx
│   │   │   ├── SectionVision.jsx
│   │   │   ├── SectionCapabilities.jsx
│   │   │   ├── SectionStudio.jsx
│   │   │   └── ContactSection.jsx
│   │   │
│   │   └── skilltest/          # Skill testing components
│   │       ├── SkillTestContainer.jsx
│   │       ├── CodeEditor.jsx
│   │       └── AntiCheatSystem.jsx
│   │
│   ├── pages/
│   │   ├── LandingPage.jsx
│   │   ├── CompanyPage.jsx
│   │   ├── CandidatePage.jsx
│   │   ├── ReviewerPage.jsx
│   │   ├── InterviewPage.jsx
│   │   ├── PassportPage.jsx
│   │   └── SystemFlowPage.jsx
│   │
│   ├── styles/
│   │   ├── globals.css         # Global styles
│   │   └── tailwind.css        # Tailwind imports
│   │
│   ├── three/                   # Three.js components
│   │   ├── index.js            # 3D scene setup
│   │   └── objects/            # 3D objects
│   │
│   ├── App.jsx                 # Main app component
│   ├── main.jsx               # Entry point
│   └── index.css              # CSS entry
│
├── public/
│   ├── fonts/                  # Custom fonts
│   └── index.html
│
├── package.json
├── vite.config.js             # Vite configuration
├── tailwind.config.js         # Tailwind configuration
├── postcss.config.js          # PostCSS configuration
└── README.md                  # This file
```

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3.1 | UI Framework |
| Vite | 6.0.3 | Build Tool & Dev Server |
| React Router | 7.13.0 | Client-side Routing |
| Tailwind CSS | 3.4.17 | Utility-first Styling |
| Framer Motion | 12.29.0 | React Animations |
| GSAP | 3.12.5 | Advanced Animations |
| Lenis | 1.1.18 | Smooth Scroll |
| Three.js | 0.170.0 | 3D Graphics |
| Auth0 | 2.15.0 | Authentication |
| Google Generative AI | 0.24.1 | AI Integration |
| Recharts | 3.7.0 | Data Visualization |
| Axios | 1.13.3 | HTTP Client |

---

## Routing

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | LandingPage | Hero with 3D scene, feature sections |
| `/company` | CompanyPage | Company dashboard wrapper |
| `/company/hiring-flow` | CompanyHiringFlow | Multi-step job creation wizard |
| `/company/dashboard` | CompanyDashboard | Job listings and statistics |
| `/company/role-pipeline` | CompanyRolePipeline | Kanban candidate pipeline |
| `/company/candidate-review` | CompanyCandidateReview | Candidate detail review |
| `/company/selected` | CompanySelectedCandidates | Final selections |
| `/candidate` | CandidatePage | Candidate dashboard wrapper |
| `/candidate/interview` | InterviewPage | AI-powered interview |
| `/passport/:id` | PassportPage | Skill passport viewer |
| `/system-flow` | SystemFlowPage | System architecture diagram |

---

## Key Features

### Candidate Experience

- **Secure Onboarding** - Auth0 integration for seamless signup
- **Application Tracking** - Live status updates for job applications
- **Skill Passport** - Cryptographically signed verification results
- **Performance Analytics** - Detailed score breakdowns and feedback
- **AI Interviews** - Real-time video sessions with Google Gemini

### Company Dashboard

- **Intelligent Matching** - AI-driven candidate matching based on verified skills
- **Audio Intelligence** - Post-interview audio summaries via ElevenLabs
- **Bias Auditing** - Real-time bias scoring for job descriptions
- **Talent Pipeline** - Visual workflow for managing candidates
- **Job Creation** - Multi-step wizard with fairness analysis

### AI Protocall Interview System

- **Real-time Video** - WebRTC-based video streaming
- **AI Analysis** - Google Gemini for conversation understanding
- **Voice Synthesis** - ElevenLabs TTS for AI responses
- **Audio Recording** - Post-interview analysis and reports
- **Theme Toggle** - Light/dark mode support

---

## API Integration

### Backend API Client

```javascript
// src/api/backend.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8010',
  headers: { 'Content-Type': 'application/json' }
});

// JWT interceptor
api.interceptors.request.use((config) => {
  const token = getAuth0AccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

### API Endpoints Used

| Category | Endpoints |
|----------|------------|
| Auth | candidateSignup, candidateLogin, companySignup, companyLogin, auth0SyncCandidate |
| Jobs | listPublishedJobs, listCompanyJobs, createJob |
| Applications | applyToJob, getApplicationStatus, submitTestResults |
| Stats | getCandidateStats, getCompanyStats, listCandidateApplications |
| Matching | runMatching, listJobApplications, listSelected |
| Review | reviewQueue, reviewAction |
| Passport | getPassport, verifyPassport |
| Bias | analyzeJobDescription |

---

## Authentication

### Auth0 Configuration

```javascript
// auth/auth0.js
export const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN,
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID,
  audience: import.meta.env.VITE_AUTH0_AUDIENCE,
  redirectUri: window.location.origin
};
```

### Auth Hook

```javascript
// Custom useAuth hook provides:
const { user, isAuthenticated, isLoading, loginWithRedirect, logout, syncWithBackend } = useAuth();
```

---

## Running the Frontend

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend running at http://localhost:8010

### Installation

```bash
cd fair-hiring-frontend
npm install
```

### Development

```bash
npm run dev
```

Runs at: `http://localhost:5173`

### Production Build

```bash
npm run build
npm run preview
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | http://localhost:8010 |
| `VITE_AUTH0_DOMAIN` | Auth0 domain | - |
| `VITE_AUTH0_CLIENT_ID` | Auth0 client ID | - |
| `VITE_AUTH0_AUDIENCE` | Auth0 API audience | - |
| `VITE_GEMINI_API_KEY` | Google Gemini API key | - |
| `VITE_ELEVENLABS_API_KEY` | ElevenLabs API key | - |

Create a `.env.local` file in the frontend root:

```
VITE_API_URL=http://localhost:8010
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=https://your-api-identifier
VITE_GEMINI_API_KEY=your-gemini-key
VITE_ELEVENLABS_API_KEY=your-elevenlabs-key
```

---

## Design Philosophy

### Premium Aesthetics
- Glassmorphism effects on cards and modals
- Smooth transitions between routes (Framer Motion)
- High-fidelity micro-animations (GSAP)
- Custom cursor with hover states

### Evidence-First UI
- Cryptographic credential visualization
- Verified skill badges and graphs
- Bias score indicators
- Match score explanations

### 3D Experience
- Interactive Three.js scene on landing page
- Parallax scrolling effects
- Responsive 3D objects

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Auth0 login fails | Check domain, client ID, and audience in .env.local |
| API connection errors | Verify backend is running on port 8010 |
| 3D scene not loading | Check Three.js initialization, browser WebGL support |
| Slow animations | Disable heavy animations on mobile devices |
| CORS errors | Configure CORS in backend main.py |

### Build Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules
rm package-lock.json
npm install
```

### Debug Mode

Add to vite.config.js:
```javascript
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173
  }
})
```

---

## Related Documentation

- [Main README](../README.md) - Project overview
- [Backend README](../backend/README.md) - FastAPI backend
- [Agent Services README](../agents_services/README.md) - Agent microservices
- [Zynd Integration README](../zynd_integration/README.md) - Zynd SDK setup

---

*Built with React + Vite + Tailwind CSS + Three.js*