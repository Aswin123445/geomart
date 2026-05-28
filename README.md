# GeoMart – Marketplace for Local Handicrafts & Geographical Products

## Overview

GeoMart is a location-driven e-commerce platform designed to connect customers with unique handicrafts and geographically specific products that are deeply connected to local culture, history, and tradition.

Many traditional products are only available within specific regions and often remain inaccessible to people outside those localities. GeoMart aims to bridge this gap by creating a digital marketplace where geographically unique products can be discovered, explored, and purchased.

Unlike traditional e-commerce platforms, GeoMart not only sells products but also preserves and shares the stories behind them.

---

# Problem Statement

Many handicraft products and culturally significant items:

* Are restricted to particular geographical regions
* Have limited market visibility
* Lose cultural identity when sold without context
* Are difficult for customers outside the locality to discover

GeoMart solves this problem by building a platform where users can:

* Discover region-specific products
* Learn the cultural story behind each product
* Purchase authentic handicraft items
* Support local communities and artisans

---

# Core Features

## Product Discovery

Users can:

* Browse geographically unique products
* Search products by category
* Filter products based on locality
* Explore traditional handicrafts

---

## Story Driven Product Pages

Each product includes:

* Product descriptions
* Origin information
* Cultural significance
* Historical background
* Artisan stories
* Locality information

This creates a shopping experience beyond simply buying products.

---

## Shopping Experience

Features include:

* Product Browsing
* Shopping Cart
* Wishlist
* Checkout System
* Order Placement
* Order Tracking

---

## Authentication System

Supports:

* User Registration
* Secure Login
* JWT Authentication
* Protected Routes
* Password Hashing
* Email Verification

---

## Product Management System

Admin functionalities include:

* Add Products
* Update Products
* Delete Products
* Manage Categories
* Add Offers
* Create Discounts
* Manage Inventory
* Upload Product Images
* Control Product Visibility

---

## Order Management

Supports:

* Create Orders
* Manage Orders
* Order Tracking
* Order History
* Status Updates

---

## Discount & Offer System

Admins can:

* Create Promotional Offers
* Apply Product Discounts
* Configure Seasonal Sales
* Manage Pricing Rules

---

# Tech Stack

## Frontend

* React
* Modern UI Components
* Responsive Design

## Backend

* FastAPI / Django Backend
* REST APIs
* Async Processing

## Database

* PostgreSQL

## Authentication

* JWT Authentication

## Background Tasks

* Celery

## Deployment

* Docker
* Cloud Deployment

---

# Project Architecture

```text
Client Application

       |

Frontend Layer

       |

API Layer

       |

Authentication Module

Product Module

Cart Module

Order Module

Offer Module

Admin Module

Story Module

       |

Database Layer

       |

Background Services
```

---

# Folder Structure

```text
geomart/

├── backend/
│
│   ├── authentication/
│   ├── products/
│   ├── orders/
│   ├── offers/
│   ├── admin/
│   ├── users/
│   ├── core/
│   └── services/
│
├── frontend/
│
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   └── assets/
│
├── docker/
├── tests/
├── README.md
└── docker-compose.yml
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>

cd geomart
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

pip install -r requirements.txt
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

# Environment Variables

Create:

```text
.env
```

Example:

```env
DATABASE_URL=

SECRET_KEY=

JWT_SECRET=

EMAIL_HOST=

REDIS_URL=
```

---

# Run Project

Backend:

```bash
uvicorn app.main:app --reload
```

Frontend:

```bash
npm run dev
```

---

# Screenshots

Add screenshots here:

* Homepage
* Product Listings
* Product Story Pages
* Shopping Cart
* Admin Dashboard
* Orders Page

---

# Future Improvements

* Interactive Product Maps
* Local Artisan Profiles
* AI Based Recommendations
* Multilingual Support
* Mobile Application
* Geographical Search

---

# Vision

GeoMart is more than an e-commerce platform.

Its vision is to preserve local culture, empower artisans, and create digital access to geographically unique products while keeping their stories alive.

---

# License

MIT License

---

# Author

**Aswin Sandeep**

Building technology that connects culture, locality, and commerce.
