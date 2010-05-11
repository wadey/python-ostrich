import json

from twisted.web.resource import Resource

from ostrich import stats

class StatsResource(Resource):
    def render_GET(self, request):
        reset = int(request.args.get('reset', [0])[0])
        return json.dumps(stats.stats(reset=reset), default=stats.json_encoder)