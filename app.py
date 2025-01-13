from flask import Flask, Response
# from database import init_db
from routes import azure_routes, user_routes, chatroom_routes
# ,test_routes

app = Flask(__name__)





app.register_blueprint(user_routes.user_routes, url_prefix='/api/v1/users')
app.register_blueprint(chatroom_routes.chatroom_routes, url_prefix='/api/v1/chatrooms')
# app.register_blueprint(test_routes.test_routes, url_prefix='/api/v1/test')
app.register_blueprint(azure_routes.azure_routes, url_prefix='/api/v1/azure')
for rule in app.url_map.iter_rules():
    print(rule,"from rules")

if __name__ == '__main__':
    app.run(debug=True)
