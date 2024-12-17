from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql

app = Flask(__name__)

def initDB():
    conn = sql.connect('database.db')
    print("Opened database successfully")   
    conn.execute('''CREATE TABLE IF NOT EXISTS ad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        ad_number TEXT,
        description TEXT,
        price REAL,
        city TEXT,
        image TEXT,
        category TEXT,
        alt_category TEXT
    );''')
    print("Table created successfully")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ad")
    if cursor.fetchone()[0] == 0:
        ad = [
            ('Toyota bZ4X', 'AD-1', 'Electric car', 50000, 'Istanbul', 'images/car1.jpeg', 'Vehicle', 'Car'),
            ('Toyota Yaris Cross', 'AD-2', 'Hybrid car', 75000, 'Ankara', 'images/car2.jpeg', 'Vehicle', 'Car'),
            ('Fiat 500', 'AD-3', 'Diesel car', 60000, 'Isparta', 'images/car3.jpeg', 'Vehicle', 'Car'),
            ('Vespa GTS 300', 'AD-4', 'Scooter, 6001 km, 300cc HPE', 17500, 'Antalya', 'images/motorcyle1.jpeg', 'Vehicle', 'Motorcycle'),
            ('Yamaha YZF R25', 'AD-5', 'Super Sport, 25204 km, 250cc', 30000, 'Izmir', 'images/motorcyle2.jpeg', 'Vehicle', 'Motorcycle'),
            ('Kuba GT5 2000', 'AD-6', 'Scooter, 7500, 300cc', 15000, 'Tekirdağ', 'images/motorcyle3.jpeg', 'Vehicle', 'Motorcycle'),
            ('Nissan Terrano', 'AD-7', 'Diesel car', 100000, 'Konya', 'images/offroad1.jpeg', 'Vehicle', 'Off Road & SUV & Pickup'),
            ('Istanbul Beşiktaş Residance', 'AD-8', '220 m2, 4+1 ', 2450000, 'Istanbul', 'images/residence1.jpeg', 'Estate', 'Residence'),
            ('Balıkesir Residence', 'AD-9', '120 m2, 1+1', 1850000, 'Balıkesir', 'images/residence2.jpeg', 'Estate', 'Residence'),
            ('Yalova Residence', 'AD-10', '100 m2, 1+0', 150000, 'Yalova', 'images/residence3.jpeg', 'Estate', 'Residence'),
            ('Office in Bodrum', 'AD-11', '120 m2 1+0', 120000, 'Muğla', 'images/workplace1.jpeg', 'Estate', 'Workplace'),
            ('Office for sale in Bomonti Business Center', 'AD-12', '240 m2, 3+1', 298000, 'Istanbul', 'images/workplace2.jpeg', 'Estate', 'Workplace'),
            ('Office for sale in Çağla Street', 'AD-13', '180 m2, 2+1', 250000, 'Izmir', 'images/workplace3.jpeg', 'Estate', 'Workplace'),
            ('Land on S.Paşa Barbaros near seaside', 'AD-14', '70 m2', 389500, 'Antalya', 'images/land1.jpeg', 'Estate', 'Land'),
            ('Land on Altındere Street', 'AD-15', '9396 m2', 1550000, 'Izmir', 'images/land2.jpeg', 'Estate', 'Land'),
            ('Desktop Pc Full Equipted', 'AD-16', 'AMD Ryzen 7 2700X', 13000, 'Istanbul', 'images/computer1.jpeg', 'Second Hand', 'Computer'),
            ('Second hand Iphone 15 Pro Max', 'AD-17', '256 GB Memory, 8 GB Ram', 41000, 'Antalya', 'images/mobilephone1.jpeg', 'Second Hand', 'Mobile Phone'),
            ('Leica C-Lux 2 7.2MP', 'AD-18', '2.5 inç, 7.0-9.9 MP resolution', 6500, 'Bursa', 'images/digitalcamera1.jpeg', 'Second Hand', 'Digital Camera'),
        ]
        
        conn.executemany('INSERT INTO ad (name, ad_number, description, price, city, image, category, alt_category) VALUES (?, ?, ?, ?, ?, ?, ?, ?);', ad)
        print("Initial records inserted successfully")
    else:
        print("Database already contains data, skipping initial insert.")
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sql.connect('database.db')
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    # Modify the query to fetch only the first 8 items
    cursor.execute("SELECT * FROM ad LIMIT 8")
    ad = cursor.fetchall()

    # Count items by subcategory
    cursor.execute("""
        SELECT alt_category, COUNT(*) as count 
        FROM ad 
        GROUP BY alt_category
    """)
    sub_category_counts = cursor.fetchall()

    # Count items by category
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM ad
        GROUP BY category
    """)
    category_counts = cursor.fetchall()

    counts = {row['alt_category']: row['count'] for row in sub_category_counts}
    category_counts_dict = {row['category']: row['count'] for row in category_counts}

    conn.close()
    return render_template('home.html', ad=ad, counts=counts, category_counts=category_counts_dict)

@app.route('/item/<int:item_id>')
def item_details(item_id):
    conn = sql.connect('database.db')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ad WHERE id = ?", (item_id,))
    ad = cursor.fetchone()
    conn.close()
    if not ad:
        return "Item not found", 404
    return render_template('itemDetails.html', ad=ad)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['search_query']
    conn = sql.connect('database.db')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ad 
        WHERE name LIKE ? OR ad_number LIKE ? OR description LIKE ? OR price LIKE ? 
        OR city LIKE ? OR category LIKE ? OR alt_category LIKE ?
    """, ('%' + query + '%', '%' + query + '%', '%' + query + '%', 
          '%' + query + '%', '%' + query + '%', '%' + query + '%', 
          '%' + query + '%'))
    results = cursor.fetchall()
    conn.close()
    return render_template('searchResults.html', query=query, results=results)

@app.route('/category/<category>/<sub_category>')
def filter_by_category_and_sub_category(category, sub_category):
    conn = sql.connect('database.db')
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM ad WHERE category = ? AND alt_category = ?", (category, sub_category))
    ads = cursor.fetchall()
    
    cursor.execute("""
        SELECT alt_category, COUNT(*) as count 
        FROM ad 
        GROUP BY alt_category
    """)
    sub_category_counts = cursor.fetchall()

    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM ad
        GROUP BY category
    """)
    category_counts = cursor.fetchall()
    
    counts = {row['alt_category']: row['count'] for row in sub_category_counts}
    category_counts_dict = {row['category']: row['count'] for row in category_counts}

    conn.close()
    return render_template('home.html', ad=ads, counts=counts, category_counts=category_counts_dict)



if __name__ == '__main__':
    initDB()
    app.run(debug=True)
