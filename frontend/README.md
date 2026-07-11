# ATLAS Platform Frontend

This directory contains the React/Next.js frontend application for the ATLAS Intelligence Platform.

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (dashboard)/       # Protected dashboard pages
│   │   ├── dashboard/     # Main dashboard
│   │   ├── opportunities/  # Opportunities management
│   │   ├── intelligence/  # Intelligence signals
│   │   ├── reports/       # Reports management
│   │   ├── notifications/ # Notifications & preferences
│   │   ├── billing/       # Billing & subscription
│   │   ├── ai-providers/  # AI provider management
│   │   ├── connectors/    # Data connectors
│   │   └── monitoring/     # System monitoring
│   ├── admin/              # Admin panel pages
│   │   ├── dashboard/      # Admin dashboard
│   │   ├── organizations/ # Organization management
│   │   ├── users/         # User management
│   │   ├── subscriptions/ # Subscription management
│   │   ├── plans/         # Plan management
│   │   ├── feature-flags/ # Feature flag management
│   │   ├── api-keys/      # API key management
│   │   └── audit-logs/    # Audit logs
│   └── auth/               # Authentication pages
│       ├── login/          # Login
│       ├── register/       # Registration
│       ├── forgot-password/ # Password recovery
│       └── reset-password/  # Password reset
├── components/             # Reusable React components
│   ├── ui/               # Base UI components
│   └── layout/            # Layout components
├── hooks/                  # React Query hooks
├── services/              # API service layer
├── store/                 # Zustand stores
├── types/                 # TypeScript types
└── lib/                   # Utility functions
```

## Features

### Core
- Next.js 14 with App Router
- React 18 with TypeScript
- Tailwind CSS with shadcn/ui components
- React Query for server state management
- Zustand for client state management
- Dark/Light mode support

### Pages
- **Dashboard**: Executive overview with KPIs, recent signals, and activity
- **Opportunities**: List, search, filter, and bookmark opportunities
- **Intelligence**: Live signals with evidence and source viewers
- **Reports**: Report management with export and scheduling
- **Notifications**: In-app notification center with preferences
- **Billing**: Subscription management, invoices, and payment methods
- **AI Providers**: Provider health, costs, and token usage monitoring
- **Connectors**: Data connector status and sync management
- **Monitoring**: System health and background job status

### Admin Panel
- **Dashboard**: System health, analytics, and quick actions
- **Organizations**: Multi-tenancy management
- **Users**: User CRUD with role management
- **Subscriptions**: Subscription lifecycle management
- **Plans**: Subscription plan configuration
- **Feature Flags**: Dynamic feature toggles
- **API Keys**: API key creation and rotation
- **Audit Logs**: Action tracking and export

### Quality
- TypeScript strict mode
- ESLint with Next.js configuration
- Jest for unit and component testing
- Comprehensive type coverage

## Development Commands

```bash
# Development
npm run dev              # Start development server
npm run lint            # Run ESLint
npm run lint:fix       # Auto-fix linting issues
npm run typecheck       # Run TypeScript type checking

# Testing
npm test                # Run tests
npm run test:watch     # Run tests in watch mode
npm run test:ci        # Run tests with coverage

# Build
npm run build           # Build for production
npm run start          # Start production server
npm run format         # Format code with Prettier
npm run format:check   # Check code formatting
```

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Integration

The frontend communicates with the backend via REST API. All API calls are made through the `apiClient` utility which handles:
- Authentication token injection
- Automatic token refresh
- Error handling

## Testing

Tests are located in `__tests__/` and include:
- Unit tests for utility functions
- Component tests for UI components
- Integration tests for page behavior

Run tests with `npm test`.
