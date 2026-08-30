// Local logic tests only: this DOM stand-in does not test browser layout or CSS.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { Script, createContext } from "node:vm";

const html = readFileSync(new URL("../visuals/set-explorer.html", import.meta.url), "utf8");
const dataText = html.match(/<script id="python-traces" type="application\/json">\s*([\s\S]*?)\s*<\/script>/)[1];
const traces = JSON.parse(dataText);
const source = html.match(/<script>\s*([\s\S]*?)\s*<\/script>/)[1];
const script = new Script(source, { filename: "set-explorer.html:inline-script" });
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);

class Element {
  constructor() {
    this.textContent = "";
    this.value = "";
    this.className = "";
    this.children = [];
    this.attributes = new Map();
    this.listeners = new Map();
  }
  replaceChildren() { this.children = []; }
  append(child) { this.children.push(child); }
  setAttribute(name, value) { this.attributes.set(name, value); }
  addEventListener(event, callback) { this.listeners.set(event, callback); }
  change(value) {
    this.value = value;
    assert.equal(typeof this.listeners.get("change"), "function");
    this.listeners.get("change")();
  }
}

function boot() {
  const nodes = new Map(ids.map(id => [id, new Element()]));
  const document = {
    getElementById(id) {
      assert.ok(nodes.has(id), `missing element: ${id}`);
      return nodes.get(id);
    },
    createElement(tag) {
      assert.equal(tag, "span");
      return new Element();
    }
  };
  nodes.get("python-traces").textContent = dataText;
  for (const id of ["scenario", "operation"]) {
    const options = html.match(new RegExp(`<select id="${id}">([\\s\\S]*?)<\\/select>`))[1];
    nodes.get(id).value = options.match(/<option value="([^"]+)"/)[1];
  }
  script.runInContext(createContext({ document }), { timeout: 1000 });
  return nodes;
}

function expectedSet(values) {
  return values.length ? "{" + values.map(value => `'${value}'`).join(", ") + "}" : "set()";
}

test("HTML IDs and controls are consistent; all code is local", () => {
  assert.equal(new Set(ids).size, ids.length);
  assert.match(html, /<label for="scenario">/);
  assert.match(html, /<label for="operation">/);
  assert.match(html, /aria-live="polite"/);
  assert.doesNotMatch(html, /<script[^>]+src=|\bfetch\(|XMLHttpRequest|WebSocket/);
  const scenarioOptions = html.match(/<select id="scenario">([\s\S]*?)<\/select>/)[1];
  assert.deepEqual([...scenarioOptions.matchAll(/value="([^"]+)"/g)].map(match => match[1]),
                   traces.map(trace => trace.id));
});

test("initial render is useful without a change event", () => {
  const nodes = boot();
  assert.equal(nodes.get("expression").textContent, "A | B");
  assert.equal(nodes.get("result-members").textContent, "{'api', 'cache', 'cron', 'worker'}");
});

const expressions = {
  union: "A | B", intersection: "A & B", difference: "A - B",
  reverse_difference: "B - A", symmetric_difference: "A ^ B"
};

for (const trace of traces) {
  for (const [operation, result] of Object.entries(trace.results)) {
    test(`${trace.id} / ${operation}: event logic, result, regions, and relations`, () => {
      const nodes = boot();
      nodes.get("scenario").change(trace.id);
      nodes.get("operation").change(operation);
      assert.equal(nodes.get("expression").textContent, expressions[operation]);
      assert.equal(nodes.get("result-members").textContent, expectedSet(result));
      assert.equal(nodes.get("left-input").textContent, expectedSet(trace.a));
      assert.equal(nodes.get("right-input").textContent, expectedSet(trace.b));
      assert.equal(nodes.get("subset").textContent, trace.subset ? "True" : "False");
      assert.equal(nodes.get("proper-subset").textContent, trace.proper_subset ? "True" : "False");
      assert.equal(nodes.get("disjoint").textContent, trace.disjoint ? "True" : "False");
      const included = [];
      for (const [region, values] of [
        ["left-only", trace.left_only], ["both", trace.both], ["right-only", trace.right_only]
      ]) {
        const children = nodes.get(region).children;
        if (!values.length) {
          assert.equal(children.length, 1);
          assert.equal(children[0].textContent, "No members");
        } else {
          assert.deepEqual(children.map(child => child.textContent), values);
        }
        for (const child of children.filter(child => child.className.includes("member"))) {
          const survives = result.includes(child.textContent);
          assert.equal(child.className.includes("included"), survives);
          assert.equal(child.attributes.get("aria-label"),
                       child.textContent + (survives ? ": included" : ": excluded"));
          if (survives) included.push(child.textContent);
        }
      }
      assert.deepEqual(included.sort(), result);
    });
  }
}
