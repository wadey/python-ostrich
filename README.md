# python-ostrich

This is a port of the Scala [Ostrich](http://github.com/robey/ostrich) library. This port is currently a work in progress, so only the stuff covered in the unit tests are considered to be completed.

NOTE: This initial version is not thread safe. My first use case is inside of a Twisted server, so I don't need thread safety right now. I hope to support this in the future.

## Stats API ##

There are three kinds of statistics that ostrich captures:

- counters
  
  A counter is a value that never decreases. Examples might be "`widgets_sold`" or "`births`". You
  just click the counter each time a countable event happens, and graphing utilities usually graph
  the deltas over time. To increment a counter, use:
 
        stats.incr("births")
        
        # or

        stats.incr("widgets_sold", 5)

- gauges

  A gauge is a value that has a discrete value at any given moment, like "`heap_used`" or
  "`current_temperature`". It's usually a measurement that you only need to take when someone asks.
  To define a gauge, stick this code somewhere in the server initialization:

        stats.make_gauge("current_temperature", lambda: my_thermometer.get_temperature_in_celcius())

        # you can also create a gauge by decorating a method:

        @stats.gauge("current_temperature")
        def current_temperature():
            return my_thermometer.get_temperature_in_celcius()

  Gauge methods should always return a number (either an integer or a float)

- timings

  A timing is a stopwatch timer around code, like so:

        with stats.time("translation"):
            document.translate("de", "en")

        # you can also time something by decorating the method:

        @stats.time("translation")
        def translation():
            document.translate("de", "en")

  Timings are collected in aggregate, and the aggregation is reported through the "`stats`" command.
  The aggregation includes the count (number of timings performed), sum, maximum, minimum, average,
  standard deviation, and sum of squares (useful for aggregating the standard deviation).

## Dump stats as JSON ##

There is a `stats.json_encoder` function provided to make dumping that stats to JSON easy.

    json.dumps(stats.stats(reset=False), default=stats.json_encoder)

## Twisted Web Resource ##

If you are using Twisted Web, there is a ready to use Resource available:

    from ostrich.twisted import StatsResource

This resource will respond to the query string parameter `reset=(0|1)`. If not specified, the default is `reset=0`.