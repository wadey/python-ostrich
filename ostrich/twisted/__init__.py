import time
import json

from twisted.web import static
from twisted.web.resource import Resource

from ostrich import stats
from ostrich.time_series_collector import TimeSeriesCollector
from ostrich.timing import TimingStat

def respond(request, data):
    data = json.dumps(data, default=stats.json_encoder)
    if 'callback' in request.args:
        request.setHeader('Content-Type', 'application/javascript')
        return request.args['callback'][0] + "(" + data + ")\n"
    else:
        request.setHeader('Content-Type', 'application/json')
        return data + "\n"

class StatsResource(Resource):
    def render_GET(self, request):
        reset = int(request.args.get('reset', [0])[0])
        data = stats.stats(reset=reset)
        return respond(request, data)

class StatsTimeSeriesResource(StatsResource):
    def __init__(self, collect_every=60):
        Resource.__init__(self)
        self.collector = TimeSeriesCollector()
        self.collector.start_twisted(collect_every=collect_every)
        
        self.putChild('graph', static.Data(GRAPH_HTML.strip(), "text/html"))
        self.putChild('graph_data', TimeSeriesDataResource(self.collector))
        self.putChild('combined', TimeSeriesCombinedResource(self.collector))
    
    # def render_GET(self, request):
    #     reset = int(request.args.get('reset', [0])[0])
    #     return json.dumps(stats.stats(reset=reset), default=stats.json_encoder)

class TimeSeriesDataResource(Resource):
    isLeaf = True
    
    def __init__(self, collector):
        self.collector = collector
    
    def render_GET(self, request):
        if len(request.postpath) == 0:
            return json.dumps({'keys': self.collector.keys(), 'stats': self.collector.stats.stats()}, default=stats.json_encoder) + "\n"
        else:
            def convert(v):
                if isinstance(v, TimingStat):
                    return ';'.join(map(str, [v.min, v.average, v.max]))
                return v

            name = request.postpath[0]
            output = "Date,%s\n" % name
            
            for date, value in self.collector.get(name):
                output += "%s,%s\n" % (time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(date)), convert(value) or '')
            
            return output

class TimeSeriesCombinedResource(Resource):
    isLeaf = True
    
    def __init__(self, collector):
        self.collector = collector
    
    def render_GET(self, request):
        if len(request.postpath) == 0:
            data = {}
            data['timings'] = dict((name, self.collector.get_combined("timing:%s" % name).to_dict()) for name in self.collector.stats.timings.keys())
            data['counters'] = dict((name, self.collector.get_combined("counter:%s" % name)) for name in self.collector.stats.counters.keys())
            return respond(request, data)
        else:
            name = request.postpath[0]
            data = self.collector.get_combined(name).to_dict()
            return respond(request, data)

GRAPH_HTML = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
  <script type="text/javascript" src="http://danvk.org/dygraphs/dygraph-combined.js"></script>
  <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js"></script>
  <script type="text/javascript">
    if (document.location.search.length > 0) {
      $(document).ready(drawChart);
    } else {
      $.getJSON("graph_data", function(datadump) {
        var keys = datadump["keys"].sort();
        for (i in keys) {
          $("#contents").append('<a href="graph?' + keys[i] + '">' + keys[i] + '</a><br/>');
        }
        $("#graph-container").css("display", "none");
      });
    }

    function drawChart() {
      var key = document.location.search.substr(1);
      g = new Dygraph(
        document.getElementById("chart"),
        "graph_data/" + key,
        {
          //rollPeriod: 1,
          showRoller: true,
          customBars: true
          //yAxisLabelWidth: 30
        }
      );
    }
  </script>
</head>
<body>

<div id="graph-container">
<div id="chart" style="width: 640px; height: 320px;"></div>
</div>
<div id="contents"></div>

</body>
</html>
"""
