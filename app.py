from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def extract_hrefs(json_data) -> set:
    """
    Extract all hrefs from the JSON data structure.
    
    If json_data is a dictionary with a key "relationships_following",
    the function will use the value of that key (an array) for processing.
    
    Args:
        json_data (list or dict): The JSON data, which can be a list of objects
                                  or an object with a "relationships_following" key.
        
    Returns:
        set: Set of unique href values.
    """
    # If the JSON is an object with a key "relationships_following", use its value.
    if isinstance(json_data, dict) and "relationships_following" in json_data:
        json_data = json_data["relationships_following"]
    
    hrefs = set()
    for item in json_data:
        if "string_list_data" in item:
            for string_data in item["string_list_data"]:
                if "href" in string_data and string_data["href"]:
                    hrefs.add(string_data["href"])
    return hrefs

def find_unique_hrefs(json1_data, json2_data) -> set:
    """
    Find hrefs that are in the first JSON data but not in the second JSON data.
    
    Args:
        json1_data (list or dict): First JSON input data.
        json2_data (list or dict): Second JSON input data.
        
    Returns:
        set: Set of unique hrefs from the first JSON.
    """
    hrefs1 = extract_hrefs(json1_data)
    hrefs2 = extract_hrefs(json2_data)
    return hrefs1 - hrefs2

@app.route('/unique_hrefs', methods=['POST'])
def unique_hrefs_endpoint():
    """
    POST endpoint that expects a JSON payload with 'json1' and 'json2' keys.
    Returns a JSON response with the unique hrefs (only the part after '.com/')
    and the total count.
    """
    data = request.get_json()
    if not data or 'json1' not in data or 'json2' not in data:
        return jsonify({"error": "Missing 'json1' or 'json2' in request data."}), 400

    json1_data = data['json1']
    json2_data = data['json2']
    
    unique_hrefs_set = find_unique_hrefs(json1_data, json2_data)
    
    # Create a list with only the part after ".com/"
    result = []
    for href in sorted(unique_hrefs_set):
        if ".com/" in href:
            result.append(href.split(".com/", 1)[1])
        else:
            result.append(href)
    
    response = {
        "unique_hrefs": result,
        "count": len(result)
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
