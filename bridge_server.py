from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive_recipe', methods=['POST'])
def receive_recipe():
    # JSON 형식으로 데이터를 받음
    recipe_data = request.json
    print(f"Received recipe: {recipe_data}")
    
    # 받은 데이터를 처리하는 로직 (예: ROS로 전달)
    
    return jsonify({"status": "Recipe received"}), 200

if __name__ == '__main__':
    app.run(port=8080, debug=True)
