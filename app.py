# filepath: /E:/stki-backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from search import search_documents, index_csv
from dotenv import load_dotenv
import os
import psutil
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load configuration based on FLASK_ENV
if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
else:
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'

# Load dataset
data_file = os.getenv('DATA_FILE')
news_data = pd.read_csv(data_file)
index_csv(data_file)

@app.route('/news', methods=['GET'])
def get_news():
    page = request.args.get('page', default=1, type=int)
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    
    # Get category from query parameters
    category = request.args.get('category', default=None, type=str)

    # Filter news data by category if provided
    if category:
        filtered_news = news_data[news_data['category'].str.lower() == category.lower()]
    else:
        filtered_news = news_data

    paginated_news = filtered_news[start:end].to_dict(orient='records')
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': len(filtered_news),
        'news': paginated_news
    })

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', default='', type=str)
    page = request.args.get('page', default=1, type=int)
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page

    results = search_documents(query, data_file)
    total_results = len(results)
    paginated_results = results[start:end]

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total_results,
        'news': paginated_results
    })

@app.route('/memory')
def memory():
    # Mendapatkan penggunaan memori saat ini
    process = psutil.Process()
    memory_usage = process.memory_info().rss / (1024 * 1024)  # dalam MB
    return jsonify({'memory_usage_mb': memory_usage})

@app.route('/news/<int:news_id>', methods=['GET'])
def get_news_by_id(news_id):
    news_item = news_data[news_data['id'] == news_id]
    
    if not news_item.empty:
        return jsonify(news_item.iloc[0].to_dict())
    else:
        return jsonify({'error': 'News item not found'}), 404

if __name__ == '__main__':
    app.run()