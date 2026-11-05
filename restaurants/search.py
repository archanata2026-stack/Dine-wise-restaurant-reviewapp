import boto3
from decouple import config
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers

INDEX = 'restaurants'


def get_client():
    host = config('OPENSEARCH_ENDPOINT', default='')
    if not host:
        return None
    auth = AWSV4SignerAuth(boto3.Session().get_credentials(), 'ap-southeast-2', 'es')
    return OpenSearch(hosts=[{'host': host, 'port': 443}], http_auth=auth, use_ssl=True,
                      verify_certs=True, connection_class=RequestsHttpConnection, timeout=15)


def index_all():
    from .models import Restaurant
    client = get_client()
    if not client.indices.exists(index=INDEX):
        client.indices.create(index=INDEX, body={'mappings': {'properties': {
            'name': {'type': 'text'}, 'cuisine': {'type': 'text'}, 'city': {'type': 'text'},
            'description': {'type': 'text'}, 'food_type': {'type': 'keyword'},
            'location': {'type': 'geo_point'}}}})

    def actions():
        for r in Restaurant.objects.all():
            doc = {'name': r.name, 'cuisine': r.cuisine, 'city': r.city,
                   'description': r.description, 'food_type': r.food_type}
            if r.latitude is not None and r.longitude is not None:
                doc['location'] = {'lat': r.latitude, 'lon': r.longitude}
            yield {'_index': INDEX, '_id': r.id, '_source': doc}

    helpers.bulk(client, actions())
    return Restaurant.objects.count()


def search(q, lat=None, lng=None, size=20):
    body = {'size': size, 'query': {'multi_match': {
        'query': q, 'fields': ['name^3', 'cuisine^2', 'city', 'description'], 'fuzziness': 'AUTO'}}}
    if lat is not None and lng is not None:
        body['sort'] = [{'_geo_distance': {'location': {'lat': lat, 'lon': lng},'order': 'asc', 'unit': 'km'}}]
    hits = get_client().search(index=INDEX, body=body)['hits']['hits']
    return [(int(h['_id']), h['sort'][0] if h.get('sort') else None) for h in hits]