# src/main.py
import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
# Remove or comment out unused imports if db is not used initially
# from src.models.user import db
# from src.routes.user import user_bp

# Import the new trading blueprint
from src.routes.trading_routes import trading_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'a_secure_random_secret_key_for_ia_trader' # Use a better secret key in production

# Register the trading blueprint with a suitable prefix, e.g., /api
app.register_blueprint(trading_bp, url_prefix='/api')

# Database configuration remains commented out for now
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)
# with app.app_context():
#     db.create_all()

# Route to serve the main index.html and other static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        # Serve specific static files if they exist (e.g., CSS, JS)
        return send_from_directory(static_folder_path, path)
    else:
        # Serve index.html for the root path or any other path not matching a static file
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Listen on 0.0.0.0 to be accessible externally if needed (e.g., via deploy_expose_port)
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True is useful for development

