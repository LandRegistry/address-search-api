from flask import jsonify, Response, request  # type: ignore
import json
import logging
import logging.config  # type: ignore
import math
from typing import Any, Dict, List, Union

from service import app, es_access

MAX_NUMBER_SEARCH_RESULTS = int(app.config['MAX_NUMBER_SEARCH_RESULTS'])
SEARCH_RESULTS_PER_PAGE = int(app.config['SEARCH_RESULTS_PER_PAGE'])

INTERNAL_SERVER_ERROR_RESPONSE_BODY = json.dumps({'error': 'Internal server error'})
JSON_CONTENT_TYPE = 'application/json'
LOGGER = logging.getLogger(__name__)

ADDRESS_NOT_FOUND_RESPONSE = Response(json.dumps({'error': 'Address not found'}), status=404, mimetype=JSON_CONTENT_TYPE)


@app.errorhandler(Exception)
def handle_server_error(error: BaseException):
    LOGGER.error('An error occurred when processing a request', exc_info=error)
    return Response(INTERNAL_SERVER_ERROR_RESPONSE_BODY, status=500, mimetype=JSON_CONTENT_TYPE)


# TODO: remove the root route when the monitoring tools can work without it
@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def healthcheck():
    errors = _check_elasticsearch_connection()
    status = 'error' if errors else 'ok'
    http_status = 500 if errors else 200

    response_body = {'status': status}
    if errors:
        response_body['errors'] = errors

    return Response(json.dumps(response_body), status=http_status, mimetype=JSON_CONTENT_TYPE)


def paginated_address_records(address_records, page_number: int) -> Dict[str, Union[List[Dict[str, Any]], int]]:
    if address_records:
        address_dicts = [hit['_source'] for hit in address_records.hits]
        nof_results = min(address_records.total, MAX_NUMBER_SEARCH_RESULTS)
        nof_pages = math.ceil(nof_results / SEARCH_RESULTS_PER_PAGE)  # 0 if no results
        page_number = min(page_number, nof_pages - 1) if nof_pages > 0 else 0  # 0 indexed
    else:
        address_dicts, nof_results, page_number = [], 0, 0
    return {'addresses': address_dicts, 'total': nof_results, 'page_number': page_number, 'page_size': SEARCH_RESULTS_PER_PAGE}


@app.route('/search', methods=['GET'])
def get_search_results() -> str:
    phrase = request.args.get('phrase')
    postcode = request.args.get('postcode')
    page_number = int(request.args.get('page_number', 0))
    page_size = int(request.args.get('page_size', SEARCH_RESULTS_PER_PAGE))

    if phrase:
        address_records = es_access.get_addresses_for_phrase(phrase, page_number)
    elif postcode:
        address_records = es_access.get_addresses_for_postcode(postcode, page_number)
    result = paginated_address_records(address_records, page_number)
    return jsonify({'data': result})


def _check_elasticsearch_connection() -> List[str]:
    """Checks elasticsearch connection and returns a list of errors"""
    try:
        status = es_access.get_info()['status']
        if status == 200:
            return []
        else:
            return ['Unexpected elasticsearch status: {}'.format(status)]
    except Exception as e:
        return ['Problem talking to elasticsearch: {0}'.format(str(e))]
