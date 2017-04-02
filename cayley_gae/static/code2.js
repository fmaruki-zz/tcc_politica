function renderPartidos(listaPartidos) {
    var partidos_ul = document.getElementById("partidos");
    var fragment = document.createDocumentFragment();
    listaPartidos.forEach(function(partido) {
        var li_partido = document.createElement("li");
        li_partido.textContent = partido.sigla;
        li_partido.setAttribute("graph_id", partido.id);
        fragment.appendChild(li_partido);
    });
    partidos_ul.innerHTML = "";
    partidos_ul.appendChild(fragment);
}

var selected_terms = {
    inner: [],
    add: function(term) {
        if(this.inner.indexOf(term) === -1) {
            this.inner.push(term);
            this.render();
        }
    },
    remove: function(term) {
        this.inner = this.inner.filter(function(a) {return a!=term});
        this.render();
    },
    select: function(term) {
        this.inner = [term];
        this.render();
    },
    has: function(term) {
        return this.inner.indexOf(term) > -1;
    },
    render: function() {
        var termos_ul = document.getElementById("assuntos");
        var fragment = document.createDocumentFragment();
        this.inner.forEach(function(termo) {
            var li_termo = document.createElement("li");
            li_termo.textContent = termo;
            fragment.appendChild(li_termo);
        });
        termos_ul.innerHTML = "";
        termos_ul.appendChild(fragment);
    }
};

var selected_partidos = {
    inner: [],
    add: function(term) {
        if(this.inner.indexOf(term) === -1) {
            this.inner.push(term);
        }
    },
    remove: function(term) {
        this.inner = this.inner.filter(function(a) {return a!=term});
    },
    select: function(term) {
        this.inner = [term];
    },
    has: function(term) {
        return this.inner.indexOf(term) > -1;
    },
    render: function() {
        jQuery("#partidos li").removeClass("selected");
        this.inner.forEach(function(partido) {
            jQuery("[graph_id='" + partido + "']").addClass("selected", true);
        });
    }
};

var wordcloud_chart = new WordCloudChart(850, 350, "#graph", function(d) {
    console.log(d3.event);
    if(d3.event.ctrlKey) {
        selected_terms.add(d.text);
    } else {
        selected_terms.select(d.text);
    }
    run("termos_by_term", {id: selected_terms.inner.join(",")})(function(data) {
        var termos = data.result.map(function(a) {return {text: a.nome, size: 10}});
        wordcloud_chart.update(termos);
    });
});

jQuery("#assuntos").on("click", "li", function() {
    selected_terms.remove(this.textContent);
});

jQuery("#password").on("change", function() {
    run("todos_partidos")(function(data) {
        renderPartidos(shuffle(data.result));
    });
});

jQuery("#partidos").on("click", "li", function(ev) {
    var partido = this.textContent;
    var graph_id = jQuery(this).attr("graph_id");
    if(selected_partidos.has(graph_id)) {
        selected_partidos.remove(graph_id);
    } else {
        if(ev.ctrlKey) {
            selected_partidos.add(graph_id);
        } else {
            selected_partidos.select(graph_id);
        }
    }
    if(selected_partidos.inner.length === 0) {
        selected_partidos.render();
        wordcloud_chart.update([]);
        return;
    }
    run("similar", {id: selected_partidos.inner[0]})(function(data) {
        var partidos = data.result;
        partidos.sort(function(a, b) {return b.qtd - a.qtd});
        renderPartidos(partidos);
        selected_partidos.render();
    });
    run("termos", {id: selected_partidos.inner.join(",")})(function(data) {
        var termos = data.result.map(function(a) {return {text: a.id.slice(1,-1), size: 10}});
        wordcloud_chart.update(termos);
    });
});

jQuery("#search").on("change", function() {
    run("search", {id: this.value})(function(data) {
        var termos = data.result.map(function(a) {return {text: a.nome, size: 10}});
        wordcloud_chart.update(termos);
    });
});
