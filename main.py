import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Dictionary to store image statistics 
image_stats = {}

CAT_API_KEY = 'live_eXC5eoZQeSxOyjPWyh5M81CfKFvjYLhNqkgVxV4zclDsTxULcB6aWpTV8Gnfbv7x'
CAT_API_URL = 'https://api.thecatapi.com/v1/images/search'  # to test rating & views use ?breed_ids=cymr


@app.route('/')
def index():
    # Fetch first cat image from the API 
    initial_image_url = get_random_cat_image()
    return render_template('index.html', url=initial_image_url)


def get_random_cat_image():
    """Fetch a random cat image from The Cat API."""
    headers = {"x-api-key": CAT_API_KEY}
    response = requests.get(CAT_API_URL, headers=headers)
    if response.status_code == 200 and response.json():
        return response.json()[0]['url']
    else:
        return None


@app.route('/get_cat', methods=['GET'])
def get_cat():
    # Fetch new image 
    new_image_url = get_random_cat_image()

    if not new_image_url:
        return jsonify(error="Unable to fetch cat image"), 500

    # Initialize stats for the new image if it doesn't exist
    if new_image_url not in image_stats:
        image_stats[new_image_url] = {'ratings': [], 'views': 0}

    # Increment the view count
    image_stats[new_image_url]['views'] += 1
    return jsonify(url=new_image_url)  # Fixed to return the image URL properly


@app.route('/rate_cat', methods=['POST'])
def rate_cat():
    image_id = request.json.get('image_id')  # Get image ID from the request
    rating = int(request.json['rating'])

    if image_id is None:
        return jsonify(error="Image ID is missing"), 400

    # Initialize stats if not present
    if image_id not in image_stats:
        image_stats[image_id] = {'ratings': [], 'views': 0}

    # Append the rating to the image's stats
    image_stats[image_id]['ratings'].append(rating)

    return jsonify(success=True)


@app.route('/get_stats', methods=['GET'])
def get_stats():
    image_id = request.args.get('image_id')  # Get image ID from the request

    if image_id is None or image_id not in image_stats:
        return jsonify(error="Image ID is missing or not found"), 400

    avg_rating = (sum(image_stats[image_id]['ratings']) / len(image_stats[image_id]['ratings'])) if \
        image_stats[image_id]['ratings'] else 0
    views = image_stats[image_id]['views']
    return jsonify({'avg_rating': round(avg_rating, 2), 'views': views})


if __name__ == "__main__":
    app.run(debug=True)
