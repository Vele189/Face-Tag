import sqlite3
from datetime import datetime

def view_database_contents():
    # Connect to SQLite database
    conn = sqlite3.connect('face_recognition.db')
    cursor = conn.cursor()
    
    # Fetch and display users
    cursor.execute("""
        SELECT id, name, age, email, phone, registered_date, image_path 
        FROM users
    """)
    users = cursor.fetchall()
    
    print("\n=== Users Database Contents ===")
    print(f"{'ID':<5} {'Name':<20} {'Age':<5} {'Email':<25} {'Phone':<15} {'Registered Date':<20} {'Image Path':<30}")
    print("-" * 120)
    
    for user in users:
        id, name, age, email, phone, reg_date, img_path = user
        print(f"{id:<5} {name:<20} {age:<5} {email or 'N/A':<25} {phone or 'N/A':<15} {reg_date:<20} {img_path or 'N/A':<30}")
    
    print("-" * 120)
    print(f"Total users: {len(users)}")
    
    # Fetch and display loyalty cards
    print("\n=== Loyalty Cards Database Contents ===")
    print(f"{'Card ID':<8} {'User ID':<8} {'Business':<15} {'Card Number':<20} {'Points':<8} {'Tier':<10} {'Registration Date':<20}")
    print("-" * 110)
    
    cursor.execute("""
        SELECT lc.*, u.name as user_name
        FROM loyalty_cards lc
        LEFT JOIN users u ON lc.user_id = u.id
        ORDER BY lc.user_id, lc.registration_date DESC
    """)
    
    loyalty_cards = cursor.fetchall()
    current_user_id = None
    
    for card in loyalty_cards:
        if current_user_id != card[1]:  # card[1] is user_id
            if current_user_id is not None:
                print("-" * 110)
            print(f"\nLoyalty cards for User: {card[-1]} (ID: {card[1]})")  # card[-1] is user_name
            print("-" * 110)
            current_user_id = card[1]
        
        print(f"{card[0]:<8} {card[1]:<8} {card[2]:<15} {card[3]:<20} {card[4]:<8} {card[5]:<10} {card[6]:<20}")
    
    print("-" * 110)
    print(f"Total loyalty cards: {len(loyalty_cards)}")
    
    # Display Rewards
    print("\n=== Available Rewards ===")
    print(f"{'ID':<5} {'Type':<10} {'Business':<15} {'Name':<25} {'Points Required':<15} {'Tier Required':<12}")
    print("-" * 85)
    
    cursor.execute("""
        SELECT id, type, business_name, name, points_required, tier_required
        FROM rewards
        WHERE active = 1
        ORDER BY business_name, points_required
    """)
    
    rewards = cursor.fetchall()
    for reward in rewards:
        id, type, business, name, points, tier = reward
        print(f"{id:<5} {type:<10} {business or 'General':<15} {name:<25} {points or 'N/A':<15} {tier or 'None':<12}")
    
    print("-" * 85)
    print(f"Total rewards: {len(rewards)}")
    
    # Display Claimed Rewards
    print("\n=== Claimed Rewards ===")
    print(f"{'User':<20} {'Reward':<25} {'Claim Date':<20} {'Expiry Date':<20} {'Status':<10}")
    print("-" * 95)
    
    cursor.execute("""
        SELECT u.name, r.name, ur.claim_date, ur.expiry_date, ur.status
        FROM user_rewards ur
        JOIN users u ON ur.user_id = u.id
        JOIN rewards r ON ur.reward_id = r.id
        ORDER BY ur.claim_date DESC
    """)
    
    claimed_rewards = cursor.fetchall()
    for claimed in claimed_rewards:
        user, reward, claim_date, expiry_date, status = claimed
        print(f"{user:<20} {reward:<25} {claim_date:<20} {expiry_date:<20} {status:<10}")
    
    print("-" * 95)
    print(f"Total claimed rewards: {len(claimed_rewards)}")
    
    # Display Points History
    print("\n=== Points History ===")
    print(f"{'User':<20} {'Business':<15} {'Points':<10} {'Type':<10} {'Date':<20} {'Description':<30}")
    print("-" * 105)
    
    cursor.execute("""
        SELECT u.name, ph.business_name, ph.points_change, ph.transaction_type,
               ph.transaction_date, ph.description
        FROM points_history ph
        JOIN users u ON ph.user_id = u.id
        ORDER BY ph.transaction_date DESC
        LIMIT 10  -- Show only last 10 transactions for brevity
    """)
    
    points_history = cursor.fetchall()
    for record in points_history:
        user, business, points, type, date, desc = record
        print(f"{user:<20} {business or 'N/A':<15} {points:<10} {type:<10} {date:<20} {desc:<30}")
    
    print("-" * 105)
    print(f"Total transactions: {len(points_history)} (showing last 10)\n")
    
    # Statistics
    print("\n=== Statistics ===")
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM loyalty_cards")
    users_with_cards = cursor.fetchone()[0]
    print(f"Users with loyalty cards: {users_with_cards} out of {len(users)}")
    
    cursor.execute("""
        SELECT business_name, 
               COUNT(*) as cards,
               SUM(points) as total_points,
               AVG(points) as avg_points
        FROM loyalty_cards 
        GROUP BY business_name
    """)
    stats = cursor.fetchall()
    print("\nBusiness Statistics:")
    for business, cards, total_points, avg_points in stats:
        print(f"- {business}:")
        print(f"  Cards: {cards}")
        print(f"  Total Points: {int(total_points)}")
        print(f"  Average Points: {int(avg_points)}")
    
    conn.close()

if __name__ == "__main__":
    view_database_contents()