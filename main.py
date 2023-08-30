from flask import Flask, request, jsonify

from database import ProductionPlanData

web_api = Flask(__name__)


@web_api.route('/productionplan', methods=['POST'])
def productionplan():
    if request.method == 'POST':
        plan: ProductionPlanData = ProductionPlanData(request.json)
        return jsonify(plan.export_plan())


if __name__ == '__main__':
    web_api.run(
        debug=True,
        host='0.0.0.0',
        port=8888
    )
