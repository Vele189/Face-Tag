import sqlite3
from datetime import datetime

def add_rewards():
    try:
        conn = sqlite3.connect('face_recognition.db')
        cursor = conn.cursor()

        # First, let's clear existing rewards to avoid duplicates
        cursor.execute("DELETE FROM rewards")

        # General rewards (not business-specific)
        general_rewards = [
            ('birthday', None, 'Birthday Bonus', 'Get 500 bonus points on your birthday', 0, None, 1),
            ('milestone', None, 'First Purchase Bonus', 'Extra 100 points on your first purchase', 0, 'Bronze', 1),
            ('tier', None, 'Silver Tier Achievement', 'Bonus 1000 points when reaching Silver', 0, 'Silver', 1),
            ('tier', None, 'Gold Tier Achievement', 'Bonus 2000 points when reaching Gold', 0, 'Gold', 1)
        ]

        # Business-specific rewards
        business_rewards = {
            'GameZone': [
                ('points', 'GameZone', 'Free Game Session', '1-hour gaming session', 1000, 'Bronze', 1),
                ('points', 'GameZone', 'Premium Gaming Gear', 'Choose any gaming accessory', 2500, 'Silver', 1),
                ('points', 'GameZone', 'Gaming Tournament Entry', 'Free entry to monthly tournament', 5000, 'Gold', 1)
            ],
            'FreshMart': [
                ('points', 'FreshMart', 'Fresh Produce Box', 'Seasonal fruits and vegetables', 800, 'Bronze', 1),
                ('points', 'FreshMart', 'Grocery Voucher', 'R200 shopping voucher', 2000, 'Silver', 1),
                ('points', 'FreshMart', 'Premium Membership', '10% off all purchases for 3 months', 4500, 'Gold', 1)
            ],
            'TechHub': [
                ('points', 'TechHub', 'Tech Support Session', '1-hour tech support', 1200, 'Bronze', 1),
                ('points', 'TechHub', 'Extended Warranty', '+6 months warranty on any purchase', 3000, 'Silver', 1),
                ('points', 'TechHub', 'Premium Setup Service', 'Complete device setup & transfer', 6000, 'Gold', 1)
            ],
            'StyleFusion': [
                ('points', 'StyleFusion', 'Style Consultation', '30-minute style consultation', 1500, 'Bronze', 1),
                ('points', 'StyleFusion', 'Personal Shopping', '2-hour personal shopping session', 3500, 'Silver', 1),
                ('points', 'StyleFusion', 'VIP Wardrobe Refresh', 'Complete wardrobe consultation', 7000, 'Gold', 1)
            ],
            'FitLife': [
                ('points', 'FitLife', 'Guest Pass', '1-day guest pass', 500, 'Bronze', 1),
                ('points', 'FitLife', 'Personal Training', '2 personal training sessions', 2000, 'Silver', 1),
                ('points', 'FitLife', 'Nutrition Plan', 'Custom nutrition plan', 4000, 'Gold', 1)
            ]
        }

        # Insert general rewards
        cursor.executemany('''
            INSERT INTO rewards (
                type, business_name, name, description, 
                points_required, tier_required, active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', general_rewards)

        # Insert business-specific rewards
        for business, rewards in business_rewards.items():
            cursor.executemany('''
                INSERT INTO rewards (
                    type, business_name, name, description, 
                    points_required, tier_required, active
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', rewards)

        # Add a birthday reward for Ndamulelo (assuming their birthday is today)
        cursor.execute('''
            INSERT INTO user_rewards (
                user_id, reward_id, claim_date, expiry_date, status
            ) 
            SELECT 
                15, -- Ndamulelo's user ID
                r.id,
                datetime('now'),
                datetime('now', '+30 days'),
                'available'
            FROM rewards r
            WHERE r.type = 'birthday'
        ''')

        conn.commit()
        
        # Print summary of added rewards
        cursor.execute("SELECT COUNT(*) FROM rewards")
        total_rewards = cursor.fetchone()[0]
        
        print("\n=== Rewards Added Successfully ===")
        print(f"Total rewards added: {total_rewards}")
        
        # Print rewards per business
        print("\nRewards per business:")
        cursor.execute("""
            SELECT business_name, COUNT(*) 
            FROM rewards 
            GROUP BY business_name
        """)
        for business, count in cursor.fetchall():
            print(f"- {business or 'General'}: {count} rewards")
            
        # Print rewards per tier
        print("\nRewards per tier:")
        cursor.execute("""
            SELECT tier_required, COUNT(*) 
            FROM rewards 
            GROUP BY tier_required
        """)
        for tier, count in cursor.fetchall():
            print(f"- {tier or 'No tier requirement'}: {count} rewards")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Ask for confirmation
    response = input("This will reset all existing rewards. Continue? (yes/no): ")
    if response.lower() == 'yes':
        add_rewards()
    else:
        print("Operation cancelled.")