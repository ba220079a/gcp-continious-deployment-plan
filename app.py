from flask import Flask, request, jsonify

app = Flask(__name__)

#sample in-memory data to store as our labware info
labware_data = {}

@app.route('/labware', methods=['GET'])
def get_labware():
    #returns the labware information
    return jsonify(labware_data), 200

@app.route('/labware', methods=['POST'])
def add_labware():
    #gains the data sent in the POST request
    new_labware = request.get_json()

    #validation to ensure our labware has a name and type
    if not new_labware.get('name') or not new_labware.get('type'):
        return jsonify({'error': 'Missing labware name or type'}), 400

    #adds the new labware to the data store
    labware_id = len(labware_data) + 1  #used for ID generation
    labware_data[labware_id] = new_labware

    return jsonify({'message': 'Labware added successfully', 'id': labware_id}), 201

if __name__ == '__main__':
    app.run(debug=True)
