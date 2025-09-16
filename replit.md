# SQL Query Optimizer and Analyzer

## Overview

This is a full-stack web application that analyzes and optimizes SQL queries. The system helps developers identify performance issues, generate optimized queries, and provides insights into database schema optimization. It focuses on MySQL/PostgreSQL database optimization with features like JSON function optimization, index recommendations, and query complexity analysis.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript using Vite as the build tool
- **UI Library**: Radix UI components with shadcn/ui design system
- **Styling**: Tailwind CSS with CSS custom properties for theming
- **State Management**: TanStack React Query for server state management
- **Routing**: Wouter for lightweight client-side routing
- **Form Handling**: React Hook Form with Zod schema validation

### Backend Architecture
- **Runtime**: Node.js with Express.js framework
- **Language**: TypeScript with ES modules
- **Database**: PostgreSQL with Drizzle ORM for type-safe database operations
- **Storage Strategy**: In-memory storage with interface abstraction for easy database migration
- **API Design**: RESTful endpoints with consistent error handling

### Data Storage Solutions
- **Database**: PostgreSQL configured through Drizzle ORM
- **Schema Management**: Drizzle migrations with shared schema definitions
- **Connection**: Neon Database serverless PostgreSQL driver
- **Type Safety**: Full end-to-end type safety with shared schema between client and server

### Core Features Architecture
- **SQL Analysis Engine**: Parses SQL queries to detect performance issues, complexity metrics, and optimization opportunities
- **Query Optimization**: Transforms SQL queries using modern techniques like JSON functions for MySQL 5.7+
- **Index Recommendations**: Analyzes query patterns to suggest optimal database indexes
- **Schema Visualization**: Displays database structure with table relationships and statistics

### Authentication and Authorization
- No authentication system implemented - designed for internal development use
- Session management placeholder exists via connect-pg-simple for future enhancement

## External Dependencies

### Database Services
- **Neon Database**: Serverless PostgreSQL hosting platform
- **Drizzle ORM**: Modern TypeScript ORM with excellent type inference

### UI and Styling
- **Radix UI**: Headless UI components for accessibility and customization
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Icon library for consistent iconography

### Development Tools
- **Vite**: Fast build tool with HMR support
- **TypeScript**: Type safety across the entire application
- **ESBuild**: Fast JavaScript bundler for production builds

### Runtime Dependencies
- **Express.js**: Web application framework
- **React Query**: Server state management and caching
- **Wouter**: Lightweight React router
- **Zod**: Runtime type validation and schema definition

### Development Environment
- **Replit Integration**: Special plugins for Replit development environment
- **Error Handling**: Runtime error overlay for development debugging