from flask import Flask, render_template, request, jsonify
from pprint import pprint
from calculate_production_plan import calculate_production_plan

app = Flask(__name__)

@app.route('/')
def index():
    """
    Render the index.html template when accessing the root URL.
    """
    return render_template('index.html')

@app.route('/productionplan', methods=['POST'])
def productionplan():
    """
    Handle the /submit endpoint. Read JSON data from the request
    and pass it to the calculate_production_plan function.
    Return the result data as a JSON response.
    """
    json_data = request.get_json()
    print("---------------------------------------------------------------------------")
    print("Input")
    pprint(json_data)
    print("---------------------------------------------------------------------------")

    success, result_data = calculate_production_plan(json_data)
    if not success:
        # In this case result data is a message
        print(result_data)
        return jsonify({"success" :False, "err_msg":result_data})

    return jsonify(result_data)


if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(host='0.0.0.0', port=8888, debug=True)
