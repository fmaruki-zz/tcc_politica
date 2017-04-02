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
    var pass = jQuery(".password").val();
    jQuery.get("/run", {
        queryName: query,
        pass: pass,
        id: values.id,
        lvl: values.lvl
    }).done(callback);
});

var diameter = window.innerWidth;
var height = window.innerHeight;

var pack = d3.pack()
    .size([diameter - 2, diameter - 2])
    .padding(5);

var svg = d3.select("#graph")
    .attr("width", diameter)
    .attr("height", diameter)
    .attr("class", "bubble");

jQuery(".password").on("change", function() {
    run("todos_partidos")(function(data) {

        data.result.forEach(function(x) {
            x.value = 30;
        });

        var root = d3.hierarchy({
                children: data.result
            })
            .sum(function(d) {
                return d.value;
            })
            .sort(function(a, b) {
                return b.value - a.value;
            });

        pack(root);
        update(root);
    });
});

function update(root) {
    root.children.forEach(function(d) {
        d.sigla = d.data.sigla;
    });
    var node = svg.selectAll(".node")
        .data(root.children, function(d) {
            return d.sigla;
        });

    var node_enter = node
        .enter().append("g")
        .attr("class", "node")
        .classed("termo", d => !!d.data.classname)
        .attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")";
        })
        .on("click", function(d) {
            async_all(
                run("similar", {
                    id: d.data.id,
                    lvl: 1
                }),
                run("similar", {
                    id: d.data.id,
                    lvl: 2
                }),
                run("similar", {
                    id: d.data.id,
                    lvl: 3
                }),
                run("termos", {
                    id: d.data.id
                })
            )(function(dd1, dd2, dd3, dd4) {

                r1 = dd1.result;
                r2 = dd2.result;
                r3 = dd3.result;
                r4 = dd4.result;
                var pp = {};
                pp[d.data.id] = {
                    sigla: d.data.sigla,
                    id: d.data.id,
                    qtd: 27
                };
                r1.forEach(function(item) {
                    item.qtd = +item.qtd + 9;
                    pp[item.id] = item;
                });
                r2.forEach(function(item) {
                    item.qtd = +item.qtd + 3;
                    if (!pp[item.id]) {
                        pp[item.id] = item;
                    } else {
                        pp[item.id].qtd += item.qtd;
                    }
                });
                r3.forEach(function(item) {
                    item.qtd = +item.qtd + 3;
                    if (!pp[item.id]) {
                        pp[item.id] = item;
                    } else {
                        pp[item.id].qtd += item.qtd;
                    }
                });
                r4.forEach(function(item) {
                    item.sigla = item.id.toUpperCase();
                    item.qtd = 10;
                    item.classname = "termo";
                    pp[item.id] = item;
                })

                var data = [];
                for (var p in pp) {
                    data.push(pp[p]);
                }

                data.forEach(function(x) {
                    x.value = x.qtd;
                });

                var root = d3.hierarchy({
                        children: data
                    })
                    .sum(function(d) {
                        return d.value;
                    })
                    .sort(function(a, b) {
                        return b.value - a.value;
                    });

                pack(root);
                update(root);
            });
        });

    node_enter.append("title")
        .text(d => d.sigla + ": " + d.value);

    node_enter.append("circle")
        .attr("r", d => d.r);

    // node_enter.append("text")
    //     .attr("dy", ".3em")
    //     .style("text-anchor", "middle")
    //     .text(d => d.data.sigla);

    node_enter.append("foreignObject")
        .style("text-anchor", "middle")
        .attr("x", d => -0.8*d.r)
        .attr("y", d => -0.6*d.r)
        .attr("width", d => 1.6*d.r)
        .attr("height", d => 2*d.r)
        .append("xhtml:p")
        .text(d => d.data.sigla)
        .attr('style', 'text-align:center;padding:2px;margin:2px;');


    // .attr('x', x - (side/2))
    // .attr('y', y - (side/2))
    // .attr('width', side)
    // .attr('height', side)



    node.select("circle").transition()
        .attr("r", d => d.r);
    node.transition().attr("transform", function(d) {
        return "translate(" + d.x + "," + d.y + ")";
    });
    node.select("text")
        .text(d => d.sigla);

    node.exit().remove();
}
