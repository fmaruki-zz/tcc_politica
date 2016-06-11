var thunkify = require("thunkify");
var co = require("co");
var gremlin = require("gremlin");
var fs = require("fs");

var client = gremlin.createClient();
var execute = thunkify(client.execute.bind(client));
var readFile = thunkify(fs.readFile);

co(function* () {
    var lines = (yield readFile("../tse/cand_2014.json")).split("\n");
    console.log(lines[0]);

    var nodes = yield execute('g.V().values("name")', {});
    console.log(nodes);
});
