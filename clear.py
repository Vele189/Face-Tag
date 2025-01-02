import sqlite3

def clear_database():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('face_recognition.db')
        cursor = conn.cursor()
        
        # Get current counts
        cursor.execute("SELECT COUNT(*) FROM users")
        initial_users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM loyalty_cards")
        initial_cards_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rewards")
        initial_rewards_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_rewards")
        initial_user_rewards_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM points_history")
        initial_points_history_count = cursor.fetchone()[0]
        
        # Delete all records from tables (order matters due to foreign key constraints)
        cursor.execute("DELETE FROM points_history")
        cursor.execute("DELETE FROM user_rewards")
        cursor.execute("DELETE FROM loyalty_cards")
        cursor.execute("DELETE FROM rewards")
        cursor.execute("DELETE FROM users")
        
        # Commit the changes
        conn.commit()
        
        print("\n=== Database Cleanup ===")
        print(f"Initial number of users: {initial_users_count}")
        print(f"Initial number of loyalty cards: {initial_cards_count}")
        print(f"Initial number of rewards: {initial_rewards_count}")
        print(f"Initial number of claimed rewards: {initial_user_rewards_count}")
        print(f"Initial number of point transactions: {initial_points_history_count}")
        print("\nAll records have been deleted successfully!")
        print("The database table structure has been preserved.")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        print("Rolling back changes...")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("\nWARNING: This will delete ALL data including:")
    print("- Users and their face encodings")
    print("- Loyalty cards and points")
    print("- Rewards and claimed rewards")
    print("- Points history")
    print("\nThis action cannot be undone!")
    response = input("\nAre you sure you want to clear all records? (yes/no): ")
    
    if response.lower() == 'yes':
        clear_database()
    else:
        print("Operation cancelled.")