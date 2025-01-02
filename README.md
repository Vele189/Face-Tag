# FaceTag - Facial Recognition Loyalty Platform

FaceTag is an innovative loyalty platform that uses facial recognition to revolutionize how customers interact with loyalty programs. By replacing traditional loyalty cards with face recognition, FaceTag provides a seamless and secure way for customers to earn and redeem rewards.

## Project Structure

### Core Files
- `splash.html` - Landing page with animated logo
- `auth.html` - User authentication and registration page
- `dashboard.html` - Main explore page with feature cards
- `loyalty.html` - Loyalty cards and rewards management
- `welcome.html` - Welcome screen after authentication

### Backend Files
- `app.py` - Main Flask application with API endpoints and database management
- `setup_database.py` - Database initialization and schema setup
- `clear.py` - Database cleanup utility
- `view_database.py` - Database contents viewer and statistics
- `register_user.py` - Sample user registration utility
- `add_rewards.py` - Rewards system initialization

## Features

### Authentication System
- Facial recognition login
- New user registration with face capture
- Secure face encoding storage

### Main Features
1. **Loyalty & Rewards** (Active)
   - Multiple business support
   - Points tracking
   - Tier system
   - Digital rewards

2. **In-App Purchases** (Coming Soon)
   - Store browsing
   - Seamless checkout
   - Purchase history

3. **Access** (Active)
   - Face as digital key
   - Venue access
   - Event entry

4. **FacePay** (Coming Soon)
   - Facial recognition payments
   - Secure transactions
   - Payment history

### Business Partners
Each with unique rewards and point systems:
- GameZone (Gaming)
- FreshMart (Grocery)
- TechHub (Electronics)
- StyleFusion (Fashion)
- FitLife (Fitness)

## Technical Details

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    email TEXT,
    phone TEXT,
    registered_date DATETIME,
    image_path TEXT,
    face_encoding BLOB NOT NULL
)
```

#### Loyalty Cards Table
```sql
CREATE TABLE loyalty_cards (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    business_name TEXT NOT NULL,
    card_number TEXT UNIQUE,
    points INTEGER DEFAULT 0,
    tier_status TEXT DEFAULT 'Bronze',
    registration_date TEXT,
    last_used TEXT
)
```

#### Rewards Tables
```sql
CREATE TABLE rewards (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    business_name TEXT,
    name TEXT NOT NULL,
    description TEXT,
    points_required INTEGER,
    tier_required TEXT,
    active BOOLEAN DEFAULT 1
)

CREATE TABLE user_rewards (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    reward_id INTEGER,
    claim_date TEXT,
    expiry_date TEXT,
    status TEXT
)

CREATE TABLE points_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    business_name TEXT,
    points_change INTEGER,
    transaction_type TEXT,
    description TEXT,
    transaction_date TEXT
)
```

### API Endpoints

#### Authentication
- `POST /api/identify` - Face recognition authentication
- `POST /api/register` - New user registration

#### Loyalty System
- `GET /api/loyalty/cards` - Get user's loyalty cards
- `POST /api/loyalty/add` - Add new loyalty card
- `GET /api/loyalty/rewards` - Get available rewards
- `POST /api/loyalty/claim-reward` - Claim a reward

### Tier System
```
Bronze (0-1,000 points)
- 1 point per R1 spent
- Basic rewards access
- Birthday rewards

Silver (1,001-5,000 points)
- 1.25x points per R1
- Priority service
- Early access sales
- All Bronze benefits

Gold (5,000+ points)
- 1.5x points per R1
- VIP benefits
- Exclusive events
- All Silver benefits
```

## Setup

### Prerequisites
```bash
pip install -r requirements.txt
```

Required packages:
- Flask
- face_recognition
- opencv-python
- numpy
- Pillow
- sqlite3

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/facetag.git
cd facetag
```

2. Initialize the database:
```bash
python setup_database.py
```

3. Add initial rewards:
```bash
python add_rewards.py
```

4. Start the Flask server:
```bash
python app.py
```

### Utility Scripts

- Clear database: `python clear.py`
- View database contents: `python view_database.py`
- Register sample users: `python register_user.py`

## Development Notes

### Front-end
- Built with vanilla HTML, CSS, and JavaScript
- Responsive design
- Dark mode interface
- Animated components

### Security
- Face encodings stored securely
- CORS configured for API access
- Input validation on both ends
- Points transaction logging

## Author
Ndamulelo

## License
[MIT License](LICENSE)

## Future Enhancements
- Mobile app development
- Business analytics dashboard
- Multi-factor authentication
- Advanced reward algorithms
- POS system integration
