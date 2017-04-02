function thunkify(fun) {
    return function() {
        var args = Array.prototype.slice.call(arguments);
        return function(callback) {
            args.push(callback);
            fun.apply(null, args);
        };
    };
}

var async_all = thunkify(function() {
    function exec_next_thunk(thunks, results, callback) {
        var thunk = thunks.shift();
        if (thunks.length > 0) {
            thunk(function(r) {
                results.push(r);
                exec_next_thunk(thunks, results, callback);
            });
        } else {
            thunk(function(r) {
                results.push(r);
                callback.apply(null, results);
            });
        }
    }
    var thunks = Array.prototype.slice.call(arguments);
    var callback = thunks.pop();
    exec_next_thunk(thunks, [], callback);
});

var run = thunkify(function(query, values, callback) {
    if (typeof values === "function") {
        callback = values;
        values = {};
    }
    var pass = jQuery("#password").val();
    jQuery.get("/run", {
        queryName: query,
        pass: pass,
        id: values.id,
        lvl: values.lvl
    }).done(callback);
});

function shuffle(array) {
    array.sort(function() {return 0.5 - Math.random()});
    return array;
}

function WordCloudChart(width, height, elem, click_callback) {
    this.width = width;
    this.height = height;
    this.chart = d3.select(elem)
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(400,200)")

    this.update = function(data) {
        max_size = d3.max(data, function(a) {
            return a.size
        });

        var color = d3.scale.linear()
            .domain([0, 1, 2, 3, 4, 5, 6, 10, 15, 20, 100])
            .range(["#ddd", "#ccc", "#bbb", "#aaa", "#999", "#888", "#777", "#666", "#555", "#444", "#333", "#222"]);

        var chart = this.chart;

        d3.layout.cloud().size([this.width - 50, this.height - 50])
            .words(data)
            .text(function(d) {
                return d.text;
            })
            .rotate(0)
            .padding(1)
            // .font('Impact')
            .fontSize(function(d) {
                return d.size * 40 / max_size;
            })
            .on("end", draw)
            .start();

        function draw(words) {
            var obj = chart.selectAll("text")
                .data(words);
            obj.enter().append("text").on("click", click_callback);
            obj.transition()
                .duration(1000)
                .style("font-size", function(d) {
                    return d.size + "px";
                })
                .style("fill", function(d, i) {
                    return "hsl(" + (360*Math.random()|0) + ", 100%, 50%)"
                    return "hsl(207, " + (d.size|0) + "%, 50%)"
                    return color(i);
                })
                .attr("text-anchor", "middle")
                .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                }).text(function(d) {
                    return d.text;
                });
            obj.exit()
                .transition()
                .duration(1000)
                .style("fill-opacity", 1e-6)
                .remove()
        }
    }
}
