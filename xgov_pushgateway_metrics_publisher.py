from flask import Flask, request, abort, jsonify
import json
import base64
import requests, io
import pandas as pd
import requests

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

app = Flask(__name__)

@app.route('/delegator', methods=['POST'])
def xgov_pushgateway_metrics_publisher():
    if not request.json:
        abort(400)
    resquest_payload = request.json
    
    total_records = None
    total_scoring_requests = None
    average_output_token_count = None
    average_input_token_count = None
    average_record_throughput = None 
    average_record_latency = None
    average_api_throughput = None 
    average_records = None

    rouge1 = None
    rouge2 = None
    rougel = None
    rougelsum = None  
    flesch_reading_ease = None
    normalized_recall = None
    normalized_precision = None
    normalized_f1 = None

    generative_ai_quality_metrics = resquest_payload["input_data"][0]["values"]["system_facts"]["generative_ai_quality"]["metrics"]
    for metric in generative_ai_quality_metrics:
        id = metric["id"]
        if id == "rouge1":
            rouge1 = metric["value"]
        if id == "rouge2":
            rouge2 = metric["value"]
        if id == "rougel":                
            rougel = metric["value"]
        if id == "rougelsum":
            rougelsum = metric["value"]
        if id == "normalized_recall":
            normalized_recall = metric["value"]            
        if id == "normalized_precision":
            normalized_precision = metric["value"]
        if id == "normalized_f1":
            normalized_f1 = metric["value"]

        if id == "flesch_reading_ease":
            flesch_reading_ease = metric["value"]                        

    model_health_metrics = resquest_payload["input_data"][0]["values"]["system_facts"]["model_health"]["metrics"]
    for metric in model_health_metrics:
        id = metric["id"]
        if id == "total_records":
            total_records = metric["value"]
        if id == "total_scoring_requests":
            total_scoring_requests = metric["value"]
        if id == "average_output_token_count":                
            average_output_token_count = metric["value"]
        if id == "average_input_token_count":
            average_input_token_count = metric["value"]
        if id == "average_record_throughput":
            average_record_throughput = metric["value"]
        if id == "average_record_latency":
            average_record_latency = metric["value"]
        if id == "average_api_throughput":                
            average_api_throughput = metric["value"]
        if id == "average_records":
            average_records = metric["value"]

    print('>>>>>>>>>>>>>')
    print('evaluation results:')
    print('total_records:'+str(total_records))
    print('total_scoring_requests:'+str(total_scoring_requests))
    print('average_output_token_count:'+str(average_output_token_count))
    print('average_input_token_count:'+str(average_input_token_count))
    print('average_record_throughput:'+str(average_record_throughput))
    print('average_record_latency:'+str(average_record_latency))
    print('average_api_throughput:'+str(average_api_throughput))
    print('average_records:'+str(average_records))
    print('rouge1:'+str(rouge1))
    print('rouge2:'+str(rouge2))
    print('rougel:'+str(rougel))
    print('rougelsum:'+str(rougelsum))
    print('flesch_reading_ease:'+str(flesch_reading_ease))
    print('normalized_recall:'+str(normalized_recall))
    print('normalized_precision:'+str(normalized_precision))
    print('normalized_f1:'+str(normalized_f1))
    print('>>>>>>>>>>>>>')    

    data = ''
    if total_records is not None: 
        data = "total_records " + str(total_records) + "\n "
    if total_scoring_requests is not None: 
        data = data + "total_scoring_requests " + str(total_scoring_requests) + "\n "
    if average_output_token_count is not None: 
        data = data + "average_output_token_count " + str(average_output_token_count) + "\n "
    if average_input_token_count is not None: 
        data = data + "average_input_token_count " + str(average_input_token_count) + "\n "
    if average_record_throughput is not None: 
        data = data + "average_record_throughput " + str(average_record_throughput) + "\n "
    if average_record_latency is not None: 
        data = data + "average_record_latency " + str(average_record_latency) + "\n "
    if average_api_throughput is not None:
        data = data + "average_api_throughput " + str(average_api_throughput) + "\n "
    if average_records is not None:
        data = data + "average_records " + str(average_records) + "\n "
    if rouge1 is not None:
        data = data + "rouge1 " + str(rouge1) + "\n "
    if rouge2 is not None:
        data = data + "rouge2 " + str(rouge2) + "\n "
    if rougel is not None:        
        data = data + "rougel " + str(rougel) + "\n "
    if rougelsum is not None:        
        data = data + "rougelsum " + str(rougelsum) + "\n "
    if flesch_reading_ease is not None:
        data = data + "flesch_reading_ease " + str(flesch_reading_ease) + "\n "
    if normalized_recall is not None:
        data = data + "normalized_recall " + str(normalized_recall) + "\n "
    if normalized_precision is not None:
        data = data + "normalized_precision " + str(normalized_precision) + "\n "
    if normalized_f1 is not None:
        data = data + "normalized_f1 " + str(normalized_f1) + "\n "

    PUSHGATEWAY = "http://grafanamonitors1.xyz.com:9091/metrics/job"
    job_url = PUSHGATEWAY + '/' + 'xgov_metrics'    

    print('>>>>>>>>>>>>>')
    print('Publishing the following data:')
    print(data)
    print('>>>>>>>>>>>>>')

    print('>>>>>>>>>>>>>')
    print('Publishing to Grafana/Prometheus')
    headers = {'X-Requested-With': 'Python requests', 'Content-type': 'text/xml'}
    r = requests.post(job_url, headers=headers, data=data)
    print(str(r.reason) + ":" + str(r.status_code))
    print('Published to Grafana/Prometheus')
    print('>>>>>>>>>>>>>')

    scoring_predictions = {
        "published": "true"
    }
    return jsonify(scoring_predictions)

if __name__ == '__main__':
    app.run(host='grafanamonitors1.xyz.com', port=9443, debug=True)