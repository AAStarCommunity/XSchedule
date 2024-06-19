from flask import Flask, jsonify
app = Flask(__name__)


@app.route('/')
def main():
    return 'AAStar XScheduler'


@app.route('/api/healthz', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run()
