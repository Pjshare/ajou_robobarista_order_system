# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import mysql.connector
import asyncio
import websockets
import json

app = Flask(__name__)

# MariaDB 연결 설정
db_config = {
    'user': 'order_service',
    'password': 'order_service',
    'host': 'localhost',
    'database': 'bst_drip_db'
}

# WebSocket 서버 URL
WS_SERVER_URL = 'ws://192.168.58.8:9090'

# DB에서 모든 레시피 이름을 가져오는 함수
def get_all_recipes():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 모든 recipe_name을 가져오는 쿼리
    query = "SELECT recipe_name FROM bst_drip_recipe"
    cursor.execute(query)
    recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    return recipes

# DB에서 레시피 정보를 가져오는 함수
def get_recipe_by_name(recipe_name):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 해당 레시피 이름으로 레시피 정보를 가져오는 쿼리
    query = "SELECT * FROM bst_drip_recipe WHERE recipe_name = %s"
    cursor.execute(query, (recipe_name,))
    recipe = cursor.fetchone()

    cursor.close()
    conn.close()

    return recipe

# WebSocket을 통해 데이터 전송하는 비동기 함수
async def send_to_websocket(order_data, recipe):
    async with websockets.connect(WS_SERVER_URL) as websocket:
        # 웹소켓으로 전송할 데이터를 구성
        message = {
            "op": "publish",
            "topic": "/drip",
            "type": "std_msgs/String",
            "msg": {
                "data": json.dumps({
                    "order": order_data,
                    "recipe": recipe
                })
            }
        }
        # 데이터를 JSON 형식으로 변환하여 웹소켓 서버로 전송
        await websocket.send(json.dumps(message))
        print(f"Data sent to WebSocket: {message}")

# 홈 페이지 (메뉴 화면)
@app.route('/')
def menu():
    # DB에서 모든 레시피 이름을 가져옴
    recipes = get_all_recipes()

    # recipes 데이터를 menu.html에 전달하여 화면에 표시
    return render_template('menu.html', recipes=recipes)

# 주문을 처리하는 경로
@app.route('/order', methods=['POST'])
def order():
    order_data = request.json
    recipe_name = order_data.get('coffee_type')

    # DB에서 레시피 정보를 조회
    recipe = get_recipe_by_name(recipe_name)

    if recipe:
        print(f"Recipe found: {recipe}")
        # 웹소켓으로 주문 및 레시피 정보 전송
        try:
            asyncio.run(send_to_websocket(order_data, recipe))
            return jsonify({"status": "Recipe sent to WebSocket", "recipe": recipe}), 200
        except Exception as e:
            print(f"Failed to send recipe to WebSocket: {e}")
            return jsonify({"status": "Failed to send recipe to WebSocket"}), 500
    else:
        return jsonify({"status": "Recipe not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
