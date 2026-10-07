"""Small read-only MCP stdio interface. No listener, dynamic command, or arbitrary fetch."""
import json
import sys
from .domain import check_domain
from .naming import propose, logo_brief
from .trademark import screening
from .io import no_duplicates

TOOLS = [
    {'name': 'propose_names', 'description': 'Ideate or rank names. Offline ergonomic score is not semantic fit or legal clearance.', 'inputSchema': {'type': 'object', 'properties': {'brief': {'type': 'object'}, 'candidates': {'type': 'array'}, 'limit': {'type': 'integer', 'minimum': 1, 'maximum': 50}}, 'required': ['brief'], 'additionalProperties': False}},
    {'name': 'check_domain', 'description': 'RDAP registration observation. live=false by default. live=true reveals domain to IANA/RDAP. No purchase availability inference.', 'inputSchema': {'type': 'object', 'properties': {'domain': {'type': 'string'}, 'live': {'type': 'boolean'}}, 'required': ['domain'], 'additionalProperties': False}},
    {'name': 'screen_trademarks', 'description': 'Screen supplied records and produce official manual search plan; never global legal clearance.', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'countries': {'type': 'array', 'items': {'type': 'string'}}, 'classes': {'type': 'array', 'items': {'type': 'integer'}}, 'records': {'type': 'array'}}, 'required': ['name', 'countries', 'classes'], 'additionalProperties': False}},
    {'name': 'prepare_logo_brief', 'description': 'Prepare logo handoff only; generates no image and calls no provider.', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'brief': {'type': 'object'}}, 'required': ['name', 'brief'], 'additionalProperties': False}},
]

def invoke(name, args):
    schema = next((x['inputSchema'] for x in TOOLS if x['name'] == name), None)
    if schema is None:
        raise ValueError('unknown tool')
    if not isinstance(args, dict) or set(args) - set(schema['properties']) or not set(schema['required']) <= set(args):
        raise ValueError('invalid tool arguments')
    if name == 'check_domain':
        if type(args.get('live', False)) is not bool:
            raise ValueError('live must be boolean')
        return check_domain(args['domain'], args.get('live', False))
    if name == 'propose_names':
        return propose(args['brief'], args.get('candidates'), args.get('limit', 5))
    if name == 'screen_trademarks':
        return screening(args['name'], args['countries'], args['classes'], args.get('records'))
    return logo_brief(args['name'], args['brief'])

def handle(request):
    if not isinstance(request, dict) or request.get('jsonrpc') != '2.0' or not isinstance(request.get('method'), str):
        return {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid request'}}
    if 'id' not in request:
        return None
    if request['id'] is not None and type(request['id']) not in (str, int):
        return {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid request id'}}
    response = {'jsonrpc': '2.0', 'id': request['id']}
    method, params = request['method'], request.get('params', {})
    if not isinstance(params, dict):
        return {**response, 'error': {'code': -32602, 'message': 'Invalid params'}}
    if method == 'initialize':
        result = {'protocolVersion': '2025-06-18', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'nameproof-kit', 'version': '0.1.0'}}
    elif method == 'ping':
        result = {}
    elif method == 'tools/list':
        result = {'tools': TOOLS}
    elif method == 'tools/call':
        try:
            value = invoke(params.get('name'), params.get('arguments', {}))
            result = {'content': [{'type': 'text', 'text': json.dumps(value, ensure_ascii=False, allow_nan=False)}], 'isError': False}
        except (ValueError, TypeError, KeyError, OSError) as exc:
            result = {'content': [{'type': 'text', 'text': str(exc)}], 'isError': True}
    else:
        return {**response, 'error': {'code': -32601, 'message': 'Method not found'}}
    return {**response, 'result': result}

def serve(instream=None, outstream=None):
    src, dst = instream or sys.stdin, outstream or sys.stdout
    while True:
        line = src.readline(2_000_001)
        if not line:
            return 0
        if len(line) > 2_000_000:
            return 2
        try:
            request = json.loads(line, object_pairs_hook=no_duplicates, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('invalid number')))
            response = handle(request)
        except (ValueError, RecursionError):
            response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Parse error'}}
        if response is not None:
            dst.write(json.dumps(response, ensure_ascii=False, allow_nan=False) + '\n')
            dst.flush()
