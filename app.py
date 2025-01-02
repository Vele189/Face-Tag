from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import face_recognition
import sqlite3
import numpy as np
import base64
from PIL import Image
import io
import os
from datetime import datetime

app = Flask(__name__)

def init_loyalty_db():
    try:
        conn = sqlite3.connect('face_recognition.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loyalty_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                business_name TEXT NOT NULL,
                card_number TEXT UNIQUE,
                points INTEGER DEFAULT 0,
                tier_status TEXT DEFAULT 'Bronze',
                registration_date TEXT,
                last_used TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        conn.close()
        print("Loyalty database initialized successfully")
    except Exception as e:
        print(f"Error initializing loyalty database: {str(e)}")

# Initialize database first
init_loyalty_db()

# Setup CORS after database initialization
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # For development only
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }
})

class DatabaseFaceRecognition:
    def __init__(self, db_path='face_recognition.db'):
        self.known_face_encodings = []
        self.known_face_metadata = []
        self.load_database(db_path)

    def load_database(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, age, email, phone, registered_date, image_path, face_encoding 
            FROM users
        """)
        users = cursor.fetchall()
        
        for user in users:
            user_id, name, age, email, phone, reg_date, img_path, db_encoding = user
            face_encoding = np.frombuffer(db_encoding, dtype=np.float64)
            self.known_face_encodings.append(face_encoding)
            self.known_face_metadata.append({
                'id': user_id,
                'name': name,
                'age': age,
                'email': email,
                'phone': phone,
                'registered_date': reg_date,
                'image_path': img_path
            })
        conn.close()

    def identify_face(self, image_data, tolerance=0.6):
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            face_locations = face_recognition.face_locations(frame)
            if not face_locations:
                return None
            
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, 
                    face_encoding,
                    tolerance=tolerance
                )
                
                if True in matches:
                    first_match_index = matches.index(True)
                    return self.known_face_metadata[first_match_index]
            
            return None
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None

# Initialize face recognition system
face_recognizer = DatabaseFaceRecognition()

@app.route('/api/identify', methods=['POST'])
def identify_face():
    try:
        image_data = request.json.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        user_info = face_recognizer.identify_face(image_data)
        
        if user_info:
            # Get user ID from database
            conn = sqlite3.connect('face_recognition.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM users 
                WHERE name = ? AND email = ?
            """, (user_info['name'], user_info['email']))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_info['id'] = result[0]  # Add user ID to response
                return jsonify({
                    'success': True,
                    'user': user_info
                })
        return jsonify({
            'success': False,
            'message': 'No face found or face not recognized'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        print("Received registration request")
        
        data = request.json
        if not data:
            print("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400

        print("Received data:", {k: v for k, v in data.items() if k != 'image'})

        required_fields = ['name', 'age', 'image']
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            print(f"Missing required fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400

        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            os.makedirs('images', exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f'images/user_{timestamp}.jpg'
            image.save(image_path)
            print(f"Image saved to {image_path}")
            
            face_frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            face_encodings = face_recognition.face_encodings(face_frame)
            
            if not face_encodings:
                print("No face detected in the image")
                os.remove(image_path)
                return jsonify({
                    'success': False,
                    'message': 'No face detected in the image'
                }), 400
            
            face_encoding = face_encodings[0]
            
            conn = sqlite3.connect('face_recognition.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (name, age, email, phone, registered_date, image_path, face_encoding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['name'],
                data['age'],
                data.get('email'),
                data.get('phone'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                image_path,
                face_encoding.tobytes()
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            print("User successfully registered in database")
            
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'user_id': user_id,
                'image_path': image_path
            })

        except Exception as e:
            print(f"Error processing image or database operation: {str(e)}")
            if 'image_path' in locals() and os.path.exists(image_path):
                os.remove(image_path)
            raise e

    except Exception as e:
        print(f"Error in registration endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/loyalty/add', methods=['POST'])
def add_loyalty_card():
    try:
        data = request.json
        required_fields = ['user_id', 'business_name', 'card_number']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = sqlite3.connect('face_recognition.db')
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = ?', (data['user_id'],))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Check if card number already exists
        cursor.execute('SELECT id FROM loyalty_cards WHERE card_number = ?', (data['card_number'],))
        existing_card = cursor.fetchone()
        
        if existing_card:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'This card number is already registered'
            }), 400
        
        initial_points = {
            'GameZone': 100,
            'FreshMart': 50,
            'TechHub': 200,
            'StyleFusion': 150,
            'FitLife': 75
        }

        cursor.execute('''
            INSERT INTO loyalty_cards 
            (user_id, business_name, card_number, points, tier_status, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['user_id'],
            data['business_name'],
            data['card_number'],
            initial_points.get(data['business_name'], 0),
            'Bronze',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        conn.commit()
        card_id = cursor.lastrowid
        
        cursor.execute('''
            SELECT * FROM loyalty_cards WHERE id = ?
        ''', (card_id,))
        
        new_card = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Loyalty card added successfully',
            'card': {
                'id': new_card[0],
                'business_name': new_card[2],
                'card_number': new_card[3],
                'points': new_card[4],
                'tier_status': new_card[5],
                'registration_date': new_card[6]
            }
        })
        
    except Exception as e:
        print(f"Error in add_loyalty_card: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/loyalty/cards', methods=['GET'])
def get_loyalty_cards():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        conn = sqlite3.connect('face_recognition.db')
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        cursor.execute('''
            SELECT * FROM loyalty_cards 
            WHERE user_id = ?
            ORDER BY registration_date DESC
        ''', (user_id,))
        
        cards = cursor.fetchall()
        conn.close()
        
        card_list = []
        for card in cards:
            card_list.append({
                'id': card[0],
                'business_name': card[2],
                'card_number': card[3],
                'points': card[4],
                'tier_status': card[5],
                'registration_date': card[6],
                'last_used': card[7] if len(card) > 7 else None
            })
        
        return jsonify({
            'success': True,
            'cards': card_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def init_rewards_db():
    try:
        conn = sqlite3.connect('face_recognition.db')
        cursor = conn.cursor()
        
        # Create rewards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,          -- 'birthday', 'milestone', 'tier', 'points'
                business_name TEXT,          -- NULL for general rewards
                name TEXT NOT NULL,
                description TEXT,
                points_required INTEGER,
                tier_required TEXT,          -- 'Bronze', 'Silver', 'Gold'
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create user rewards table (for tracking claimed rewards)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reward_id INTEGER,
                claim_date TEXT,
                expiry_date TEXT,
                status TEXT,               -- 'claimed', 'used', 'expired'
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (reward_id) REFERENCES rewards (id)
            )
        ''')
        
        # Create points history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS points_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                business_name TEXT,
                points_change INTEGER,      -- Can be positive or negative
                transaction_type TEXT,      -- 'earn', 'redeem', 'expire'
                description TEXT,
                transaction_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("Rewards database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing rewards database: {str(e)}")
    finally:
        conn.close()

@app.route('/api/loyalty/rewards', methods=['GET'])
@app.route('/api/loyalty/rewards', methods=['GET'])
def get_rewards():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        conn = sqlite3.connect('face_recognition.db')
        cursor = conn.cursor()

        # Get user's total points and determine tier
        cursor.execute('SELECT SUM(points) FROM loyalty_cards WHERE user_id = ?', (user_id,))
        total_points = cursor.fetchone()[0] or 0
        tier = calculate_tier(total_points)

        # Get all eligible rewards based on user's tier
        cursor.execute('''
            SELECT 
                r.id,
                r.type,
                r.business_name,
                r.name,
                r.description,
                r.points_required,
                r.tier_required,
                CASE 
                    WHEN ur.id IS NOT NULL THEN 'claimed'
                    ELSE 'available'
                END as status
            FROM rewards r
            LEFT JOIN user_rewards ur ON 
                r.id = ur.reward_id AND 
                ur.user_id = ? AND 
                ur.status != 'expired'
            WHERE 
                r.active = 1
                AND (
                    r.tier_required IS NULL 
                    OR (
                        CASE 
                            WHEN r.tier_required = 'Bronze' THEN 1
                            WHEN r.tier_required = 'Silver' THEN 2
                            WHEN r.tier_required = 'Gold' THEN 3
                        END <= 
                        CASE 
                            WHEN ? = 'Bronze' THEN 1
                            WHEN ? = 'Silver' THEN 2
                            WHEN ? = 'Gold' THEN 3
                        END
                    )
                )
                AND (r.points_required <= ?)
                AND (ur.id IS NULL)  -- Only show unclaimed rewards
        ''', (user_id, tier, tier, tier, total_points))

        available_rewards = []
        for reward in cursor.fetchall():
            available_rewards.append({
                'id': reward[0],
                'type': reward[1],
                'business_name': reward[2],
                'name': reward[3],
                'description': reward[4],
                'points_required': reward[5],
                'tier_required': reward[6],
                'status': reward[7],
                'icon': get_reward_icon(reward[1])
            })

        conn.close()

        return jsonify({
            'success': True,
            'total_points': total_points,
            'current_tier': tier,
            'rewards': available_rewards
        })

    except Exception as e:
        print(f"Error getting rewards: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/loyalty/claim-reward', methods=['POST'])
def claim_reward():
    try:
        data = request.json
        user_id = data.get('user_id')
        reward_id = data.get('reward_id')

        if not user_id or not reward_id:
            return jsonify({'error': 'Missing required fields'}), 400

        conn = sqlite3.connect('face_recognition.db')
        cursor = conn.cursor()

        # Check if reward exists and is available
        cursor.execute('''
            SELECT * FROM rewards 
            WHERE id = ? AND active = 1
        ''', (reward_id,))
        reward = cursor.fetchone()

        if not reward:
            return jsonify({'error': 'Reward not found or inactive'}), 404

        # Check if user has already claimed this reward
        cursor.execute('''
            SELECT * FROM user_rewards 
            WHERE user_id = ? AND reward_id = ? AND status = 'claimed'
        ''', (user_id, reward_id))
        
        if cursor.fetchone():
            return jsonify({'error': 'Reward already claimed'}), 400

        # Calculate expiry date (30 days from claim)
        expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

        # Record the claim
        cursor.execute('''
            INSERT INTO user_rewards (user_id, reward_id, claim_date, expiry_date, status)
            VALUES (?, ?, datetime('now'), ?, 'claimed')
        ''', (user_id, reward_id, expiry_date))

        # If it's a points reward, add to points history
        if reward[1] == 'points':
            cursor.execute('''
                INSERT INTO points_history (
                    user_id, points_change, transaction_type, 
                    description, transaction_date
                )
                VALUES (?, ?, 'redeem', ?, datetime('now'))
            ''', (user_id, -reward[5], f"Claimed reward: {reward[3]}"))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Reward claimed successfully',
            'expiryDate': expiry_date
        })

    except Exception as e:
        print(f"Error claiming reward: {str(e)}")
        return jsonify({'error': str(e)}), 500

def calculate_point_value(points, tier):
    # Convert points to monetary value based on tier
    conversion_rates = {
        'Bronze': 100,  # 100 points = R1
        'Silver': 80,   # 80 points = R1
        'Gold': 50      # 50 points = R1
    }
    rate = conversion_rates.get(tier, 100)
    return points / rate

def get_reward_icon(reward_type):
    icons = {
        'birthday': '🎂',
        'milestone': '🎯',
        'tier': '⭐',
        'points': '💰'
    }
    return icons.get(reward_type, '🎁')

if __name__ == '__main__':
    init_loyalty_db()
    init_rewards_db()  # Add this line
    app.run(debug=True, port=5000)