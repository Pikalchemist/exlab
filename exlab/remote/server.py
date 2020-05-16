'''
    Author: Alexandre Manoury
    Python Version: 3.6
'''

from exlab.modular.module import Module

from flask import Flask, jsonify, request
from flask_cors import CORS

import threading
import copy


class Server(Module):
    PORT = 25010

    def __init__(self, parent=None):
        """
        Creates and starts the flask server in a seperate thread
        :param experiment: The parent module
        """
        super().__init__('Remote server', parent)
        self.parent = parent

        app = Flask(__name__)
        app.debug = False
        CORS(app)

        @app.route('/sync', methods=['GET'])
        def sync():
            return jsonify(self.manage_request())

        def flaskThread():
            app.run(host='0.0.0.0', port=self.PORT)
        self.thread = threading.Thread(target=flaskThread)
        self.thread.setDaemon(True)
        self.thread.start()

        self.logger.info("Server started")

    def manage_request(self):
        return {}
