package cayleyappengine

import (
	"encoding/json"
	// "fmt"
	"github.com/cayleygraph/cayley"
	"github.com/cayleygraph/cayley/graph"
	_ "github.com/cayleygraph/cayley/graph/memstore"
	"github.com/cayleygraph/cayley/graph/path"
	"github.com/cayleygraph/cayley/quad"
	"github.com/cayleygraph/cayley/quad/nquads"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

type tInfo map[string]string
type ByWeight []tInfo

func (s ByWeight) Len() int {
	return len(s)
}
func (s ByWeight) Swap(i, j int) {
	s[i], s[j] = s[j], s[i]
}
func (s ByWeight) Less(i, j int) bool {
	pi, _ := strconv.ParseFloat(s[i]["peso"], 64)
	pj, _ := strconv.ParseFloat(s[j]["peso"], 64)
	return pi < pj
}

func getNodeInfo(it graph.Iterator, store *cayley.Handle) tInfo {
	tags := make(map[string]graph.Value)
	it.TagResults(tags)
	info := make(tInfo)
	for tagKey, tagId := range tags {
		tagValue := store.NameOf(tagId).String()
		info[tagKey] = tagValue[1 : len(tagValue)-1]
	}
	info["id"] = store.NameOf(it.Result()).String()
	return info
}

func ApplyPath(p *path.Path, dsl string) *path.Path {
	if p == nil {
		p = path.NewPath(nil)
	}
	commands := strings.Split(dsl, " ")
	for _, command := range commands {
		action := command[0]
		value := command[1:]
		if action == '+' {
			p = p.Out(quad.IRI(value))
		} else if action == '-' {
			p = p.In(quad.IRI(value))
		} else if action == '#' {
			p = p.Save(quad.IRI(value), value)
		}
	}
	return p
}

func ApplyPathHas(store *cayley.Handle, key string, value string, dsl string) *path.Path {
	return ApplyPath(path.NewPath(store).Has(quad.IRI(key), quad.String(value)), dsl)
}

func toFloat(xs string) float64 {
	xf, _ := strconv.ParseFloat(xs, 64)
	return xf
}

func fromFloat(xf float64) string {
	return strconv.FormatFloat(xf, 'f', 6, 64)
}

func iterate(p *path.Path, store *cayley.Handle, callback func(tInfo)) {
	it := p.BuildIterator()
	for it.Next() {
		info := getNodeInfo(it, store)
		callback(info)
	}
}

func init() {
	store, err := cayley.NewGraph("memstore", "", nil)
	loadGraph(store, "./output_quads.nq")
	if err != nil {
		log.Fatalln(err)
	}
	terms_bytes, err := ioutil.ReadFile("./run.json.compact")
	if err != nil {
		log.Fatalln(err)
	}
	terms_string := string(terms_bytes)
	http.HandleFunc("/run", func(w http.ResponseWriter, r *http.Request) {
		// pass := r.URL.Query().Get("pass")
		// if pass != "titan" {
		// 	log.Fatalln(pass)
		// }
		queryName := r.URL.Query().Get("queryName")
		var results []tInfo
		switch queryName {
		case "todos_partidos":
			p := ApplyPathHas(store, "tipo", "partido", "#sigla")
			iterate(p, store, func(info tInfo) {
				results = append(results, info)
			})
			break
		case "partidos_by_term":
			id_str := r.URL.Query().Get("id")
			ids := strings.Split(id_str, ",")
			counter := make(map[string]float64)
			infos := make(map[string](tInfo))
			for _, id := range ids {
				p := ApplyPath(path.NewPath(store).Has(quad.IRI("nome"), quad.String(id)), "-termo_partido -peso_termo_partido #sigla")
				iterate(p, store, func(info tInfo) {
					infos[info["id"]] = info
					counter[info["id"]] += 1
				})
			}
			for sigla, info := range infos {
				info["peso"] = fromFloat(counter[sigla])
				results = append(results, info)
			}
			sort.Sort(sort.Reverse(ByWeight(results)))
			break
		case "artigos_by_term":
			id := r.URL.Query().Get("id")
			p := ApplyPath(path.NewPath(store).Has(quad.IRI("nome"), quad.String(id)), "-termo_artigo -peso_termo_artigo #titulo")
			it := p.BuildIterator()
			for it.Next() {
				info := getNodeInfo(it, store)
				results = append(results, info)
			}
			break
		case "termos_by_term":
			id_str := r.URL.Query().Get("id")
			ids := strings.Split(id_str, ",")
			counter := make(map[string]float64)
			infos := make(map[string](tInfo))
			p_template := ApplyPath(nil, "-termo_artigo -peso_termo_artigo +peso_termo_artigo #peso +termo_artigo #nome")
			for _, id := range ids {
				p := path.NewPath(store).Has(quad.IRI("nome"), quad.String(id)).Follow(p_template)
				iterate(p, store, func(info tInfo) {
					infos[info["id"]] = info
					counter[info["id"]] += toFloat(info["peso"])
				})
			}
			for sigla, info := range infos {
				info["peso"] = fromFloat(counter[sigla])
				results = append(results, info)
			}
			sort.Sort(sort.Reverse(ByWeight(results)))
			if len(results) > 20 {
				results = results[0:20]
			}
			break
		case "similar":
			id := r.URL.Query().Get("id")
			counter := make(map[string]int)
			infos := make(map[string](tInfo))
			similar := ApplyPath(path.NewPath(nil), "+similar #sigla")
			p1 := path.StartPath(store, quad.Raw(id)).Follow(similar)
			p2 := p1.Follow(similar)
			p3 := p2.Follow(similar)
			p_todos := path.NewPath(store).Has(quad.IRI("tipo"), quad.String("partido")).Save(quad.IRI("sigla"), "sigla")
			it_todos := p_todos.BuildIterator()
			for it_todos.Next() {
				info := getNodeInfo(it_todos, store)
				infos[info["sigla"]] = info
				counter[info["sigla"]] += 1
				if info["id"] == id {
					counter[info["sigla"]] += 999
				}
			}
			it1 := p1.BuildIterator()
			for it1.Next() {
				info := getNodeInfo(it1, store)
				counter[info["sigla"]] += 28
			}
			it2 := p2.BuildIterator()
			for it2.Next() {
				info := getNodeInfo(it2, store)
				counter[info["sigla"]] += 9
			}
			it3 := p3.BuildIterator()
			for it3.Next() {
				info := getNodeInfo(it3, store)
				counter[info["sigla"]] += 1
			}
			for sigla, info := range infos {
				info["qtd"] = strconv.Itoa(counter[sigla])
				results = append(results, info)
			}
			break
		case "search":
			text := r.URL.Query().Get("id")
			rg, _ := regexp.Compile("(?i)(.*" + text + ".*)\t(.+)")
			matches := rg.FindAllStringSubmatch(terms_string, -1)
			max_results := 30
			for _, match := range matches {
				results = append(results, tInfo{"id": match[2], "nome": match[1]})
				max_results -= 1
				if max_results <= 0 {
					break
				}
			}
			break
		case "termos":
			id_str := r.URL.Query().Get("id")
			ids := strings.Split(id_str, ",")
			counter := make(map[string]float64)
			infos := make(map[string](tInfo))
			p_template := ApplyPath(path.NewPath(nil), "+peso_termo_partido #peso +termo_partido +nome")
			for _, id := range ids {
				p := path.StartPath(store, quad.Raw(id)).Follow(p_template)
				it := p.BuildIterator()
				for it.Next() {
					info := getNodeInfo(it, store)
					infos[info["id"]] = info
					counter[info["id"]] += toFloat(info["peso"])
				}
			}
			for sigla, info := range infos {
				info["peso"] = fromFloat(counter[sigla])
				results = append(results, info)
			}

			sort.Sort(sort.Reverse(ByWeight(results)))
			results = results[0:20]
			break
		}
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		json.NewEncoder(w).Encode(map[string]interface{}{"result": results})
	})
	http.HandleFunc("/graph", func(w http.ResponseWriter, r *http.Request) {
		file, _ := ioutil.ReadFile("graph.html")
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write(file)
	})
	http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		file, _ := ioutil.ReadFile("graph.html")
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write(file)
	})
}

func loadGraph(store *cayley.Handle, filename string) {
	file, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	dec := nquads.NewDecoder(file)
	for {
		quad, err := dec.Unmarshal()
		if err != nil {
			if err != io.EOF {
				log.Fatal(err)
			}
			break
		}
		if !quad.IsValid() {
			log.Fatal("invalid")
		}
		store.AddQuad(quad)
	}
}
