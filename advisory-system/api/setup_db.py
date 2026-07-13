import sqlite3
import os

def setup_database(db_path="agri_data.db"):
    print(f"Setting up database at {db_path}...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table for structural agricultural data (e.g., market prices, weather)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crop_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            optimal_planting_season TEXT,
            average_growth_days INTEGER,
            water_requirements TEXT
        )
    """)
    
    # Create table for extension officer farm visits
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farm_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT NOT NULL,
            location TEXT NOT NULL,
            visit_date TEXT NOT NULL,
            observed_issues TEXT,
            recommended_actions TEXT
        )
    """)
    
    # Insert some dummy data for crops
    cursor.execute("SELECT COUNT(*) FROM crop_metadata")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO crop_metadata (crop_name, optimal_planting_season, average_growth_days, water_requirements)
            VALUES (?, ?, ?, ?)
        """, [
            ("Cassava", "Early Rainy Season (March - May)", 300, "Low to Moderate"),
            ("Maize", "Rainy Season (April - June)", 90, "Moderate to High"),
            ("Yam", "End of Rainy Season (November - January)", 240, "Moderate")
        ])
        
    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()
