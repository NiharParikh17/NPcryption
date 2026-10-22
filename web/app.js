"use strict";

// Every RSA number on the page comes from web/demo.py, which runs the real
// NPcryption wheel inside Pyodide. This file handles input and rendering.

const MAX_PRIME = 9973;
const THEME_KEY = "npcryption-theme";

const state = {
  p: 17,
  q: 19,
  e: 5,
  message: "Hello, RSA!",
  cipher: "",
  cipherEdited: false,
  primesChanged: false,
  exponentNote: "",
  encIndex: 0,
  decIndex: 0,
};

let py = null;
let previousBlocks = [];
let scheduled = 0;

const $ = (selector) => document.querySelector(selector);
const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

function h(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value === true ? "" : value);
  }
  node.append(...toNodes(children));
  return node;
}

// Flattens nested arrays, skips null/false, and turns strings and numbers into text.
function toNodes(children) {
  return children.flat(Infinity)
    .filter((child) => child !== null && child !== undefined && child !== false)
    .map((child) => (child instanceof Node ? child : document.createTextNode(String(child))));
}

function fill(node, ...children) {
  node.replaceChildren(...toNodes(children));
}

const num = (value, cls = "num") => h("span", { class: cls }, String(value));
const pub = (value) => num(value, "num is-public");
const priv = (value) => num(value, "num is-private");

// Long products are shortened in the middle; the full value stays in the tooltip.
function bigNum(value) {
  const text = String(value);
  if (text.length <= 22) return num(text);
  return h("span", { class: "num", title: text },
    `${text.slice(0, 9)}…${text.slice(-7)}`, h("span", { class: "visually-hidden" }, ` (${text.length} digits)`));
}

// Control characters (which wrong keys often decrypt to) are shown as their
// Unicode "control picture" so they stay visible.
function visible(text) {
  return Array.from(text, (character) => {
    const code = character.codePointAt(0);
    if (code < 32) return String.fromCodePoint(0x2400 + code);
    return code === 127 ? "␡" : character;
  }).join("");
}

function charLabel(character) {
  if (character === " ") return h("span", { class: "space-glyph", "aria-hidden": "true" }, "␣");
  return visible(character);
}

function charName(character) {
  return character === " " ? "space" : `“${visible(character)}”`;
}

function quoted(character) {
  return character === " " ? "a space" : `“${visible(character)}”`;
}

// Theme

function setupTheme() {
  const root = document.documentElement;
  const button = $("#theme-toggle");
  const update = () => {
    const dark = root.dataset.theme === "dark";
    button.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
  };
  update();
  button.addEventListener("click", () => {
    root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
    try { localStorage.setItem(THEME_KEY, root.dataset.theme); } catch (e) { /* storage unavailable */ }
    update();
  });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (event) => {
    let stored = null;
    try { stored = localStorage.getItem(THEME_KEY); } catch (e) { /* storage unavailable */ }
    if (stored) return;
    root.dataset.theme = event.matches ? "dark" : "light";
    update();
  });
}

// Python

function setStatus(kind, text) {
  $("#status").dataset.state = kind;
  $("#status-text").textContent = text;
  $("#retry").hidden = kind !== "error";
}

async function fetchOk(url, kind) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`couldn't load ${url} (HTTP ${response.status})`);
  return response[kind]();
}

async function startPython() {
  try {
    if (typeof loadPyodide !== "function") throw new Error("the Pyodide runtime didn't load");
    const [pyodide, wheel, source] = await Promise.all([
      loadPyodide(),
      fetchOk("npcryption.whl", "arrayBuffer"),
      fetchOk("demo.py", "text"),
    ]);
    pyodide.unpackArchive(wheel, "wheel");
    pyodide.runPython(source);
    const call = pyodide.globals.get("call");
    py = (action, ...args) => JSON.parse(call(action, ...args));
    const { version } = py("info");
    const python = pyodide.runPython("import sys; sys.version.split()[0]");
    setStatus("ready", `NPcryption ${version} is running in your browser.`);
    $("#footer-meta").textContent = `Runs NPcryption ${version} on Python ${python} with Pyodide ${pyodide.version}.`;
    render();
  } catch (error) {
    setStatus("error", `Python couldn't start: ${error.message}. Check your connection, then try again.`);
  }
}

// Input

function isPrime(n) {
  if (n < 2) return false;
  for (let d = 2; d * d <= n; d += 1) if (n % d === 0) return false;
  return true;
}

function stepPrime(n, direction) {
  let candidate = (Number.isFinite(n) ? n : 2) + direction;
  while (candidate >= 2 && candidate <= MAX_PRIME && !isPrime(candidate)) candidate += direction;
  return candidate >= 2 && candidate <= MAX_PRIME ? candidate : n;
}

const toInt = (value) => {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : 0;
};

function schedule() {
  clearTimeout(scheduled);
  scheduled = setTimeout(render, 80);
}

function setPrimes(p, q) {
  state.p = p;
  state.q = q;
  state.primesChanged = true;
  $("#prime-p").value = p;
  $("#prime-q").value = q;
  schedule();
}

function setExponent(e) {
  state.e = e;
  state.exponentNote = "";
  schedule();
}

function setupInputs() {
  document.querySelectorAll("[data-message]").forEach((input) => {
    input.addEventListener("input", () => {
      state.message = input.value;
      document.querySelectorAll("[data-message]").forEach((other) => {
        if (other !== input) other.value = input.value;
      });
      schedule();
    });
  });

  $("#prime-p").addEventListener("input", (event) => {
    state.p = toInt(event.target.value);
    state.primesChanged = true;
    schedule();
  });
  $("#prime-q").addEventListener("input", (event) => {
    state.q = toInt(event.target.value);
    state.primesChanged = true;
    schedule();
  });

  document.querySelectorAll("[data-prime]").forEach((button) => {
    button.addEventListener("click", () => {
      const field = button.dataset.prime;
      const next = stepPrime(state[field], Number(button.dataset.dir));
      if (field === "p") setPrimes(next, state.q);
      else setPrimes(state.p, next);
    });
  });

  document.querySelectorAll(".presets .chip").forEach((chip) => {
    chip.addEventListener("click", () => setPrimes(Number(chip.dataset.p), Number(chip.dataset.q)));
  });

  $("#exponent").addEventListener("input", (event) => setExponent(toInt(event.target.value)));

  $("#ciphertext").addEventListener("input", (event) => {
    state.cipher = event.target.value;
    state.cipherEdited = true;
    schedule();
  });

  $("#use-cipher").addEventListener("click", () => {
    state.cipherEdited = false;
    render();
  });

  $("#copy-cipher").addEventListener("click", async (event) => {
    const button = event.currentTarget;
    try {
      await navigator.clipboard.writeText(button.dataset.value || "");
      button.textContent = "Copied";
    } catch (e) {
      button.textContent = "Copy failed";
    }
    setTimeout(() => { button.textContent = "Copy"; }, 1500);
  });

  $("#retry").addEventListener("click", () => location.reload());
}

// Rendering

function render() {
  document.querySelectorAll(".presets .chip").forEach((chip) => {
    const active = Number(chip.dataset.p) === state.p && Number(chip.dataset.q) === state.q;
    chip.setAttribute("aria-pressed", String(active));
  });

  if (!py) {
    renderHeroPending();
    return;
  }

  let encrypted = py("encrypt", state.p, state.q, state.e, state.message);
  // New primes can invalidate the current E; switch to the first one that works.
  const { errors, choices = [] } = encrypted.keys;
  if (state.primesChanged) state.exponentNote = "";
  if (state.primesChanged && errors.e && !errors.p && !errors.q && choices.length) {
    state.exponentNote = `E changed from ${state.e} to ${choices[0]}, because ${state.e} doesn't work with these primes.`;
    state.e = choices[0];
    $("#exponent").value = state.e;
    encrypted = py("encrypt", state.p, state.q, state.e, state.message);
  }
  state.primesChanged = false;
  $("#exponent-note").textContent = state.exponentNote;
  const key = encrypted.keys;
  renderKeys(key, encrypted);

  if (Object.keys(key.errors).length) {
    renderBlocked();
    return;
  }

  if (!state.cipherEdited) {
    state.cipher = encrypted.ciphertext;
    $("#ciphertext").value = state.cipher;
  }
  const decrypted = py("decrypt", state.p, state.q, state.e, state.cipher);
  const cracked = py("crack", state.p, state.q, state.e);

  renderHero(encrypted);
  renderEncrypt(encrypted);
  renderDecrypt(decrypted, encrypted);
  renderToy(cracked, encrypted);
}

function renderHeroPending() {
  const strip = $("#hero-strip");
  fill(strip, ...Array.from(state.message).map((character) =>
    h("div", { class: "column pending" },
      h("span", { class: "column-char" }, charLabel(character)),
      h("span", { class: "column-code" }, "000"),
      h("span", { class: "column-block" }, "000"))));
}

function renderKeys(key, encrypted) {
  for (const field of ["p", "q", "e"]) {
    const message = key.errors[field] || "";
    $(`#error-${field}`).textContent = message;
    const input = $(field === "e" ? "#exponent" : `#prime-${field}`);
    input.closest(".field").classList.toggle("invalid", Boolean(message));
    input.setAttribute("aria-invalid", String(Boolean(message)));
  }

  const hasN = key.n !== undefined;
  $("#ring-n").textContent = hasN ? key.n : "–";
  $("#ring-e").textContent = key.d !== undefined ? key.e : "–";
  $("#ring-d").textContent = key.d !== undefined ? key.d : "–";

  const equations = $("#prime-equations");
  const note = $("#prime-note");
  note.classList.remove("warning");
  if (!hasN) {
    fill(equations);
    note.textContent = "";
  } else {
    fill(equations,
      h("p", { class: "equation" }, h("span", { class: "label is-public" }, "N"),
        ` = P × Q = ${key.p} × ${key.q} = `, pub(key.n)),
      h("p", { class: "equation" }, h("span", { class: "label is-private" }, "φ(N)"),
        ` = (P − 1) × (Q − 1) = ${key.p - 1} × ${key.q - 1} = `, priv(key.phi)));
    const tooBig = (encrypted.chars || []).find((c) => !c.fits);
    if (tooBig) {
      note.classList.add("warning");
      fill(note, `${charName(tooBig.char)} has code ${tooBig.code}, which isn't below N = ${key.n}, so it can't be decrypted correctly. Pick primes whose product is larger than ${tooBig.code}.`);
    } else {
      note.textContent = `N has ${key.width} digit${key.width === 1 ? "" : "s"}, so every character becomes a ${key.width}-digit block. Characters with a code of ${key.n} or more can't be encrypted with these primes.`;
    }
  }

  const chips = $("#exponent-choices");
  fill(chips, ...(key.choices || []).map((choice) =>
    h("button", {
      type: "button", class: "chip", "aria-pressed": String(choice === state.e),
      onclick: () => { $("#exponent").value = choice; setExponent(choice); },
    }, String(choice))));

  const panel = $("#euclid-panel");
  panel.hidden = key.d === undefined;
  if (key.d === undefined) return;

  const rows = key.euclid;
  fill($("#euclid-table tbody"), ...rows.map((row, index) =>
    h("tr", { class: index === rows.length - 1 ? "final" : null },
      h("td", {}, String(row.r)),
      h("td", {}, index < 2 ? "–" : String(row.q)),
      h("td", {}, String(row.x)),
      h("td", { class: "col-d" }, String(row.d)))));

  const last = rows[rows.length - 1];
  const factor = (n) => (n < 0 ? `(${n})` : String(n));
  const check = (BigInt(key.e) * BigInt(key.d)) % BigInt(key.phi);
  fill($("#euclid-result"),
    "The remainder reached 1, so ", num(`${key.phi} × ${factor(last.x)} + ${key.e} × ${factor(last.d)} = 1`), ". ",
    last.d < 0
      ? h("span", {}, "That D is negative, so add φ(N): ", num(`${last.d} + ${key.phi}`), " gives ")
      : "So ",
    h("strong", { class: "is-private" }, `D = ${key.d}`), ". Check: ",
    num(`${key.e} × ${key.d} mod ${key.phi} = ${check}`), ".");
}

function renderBlocked() {
  const message = "Fix the keys in steps 1 and 2 to continue.";
  fill($("#hero-strip"), ...Array.from(state.message).map((character) =>
    h("div", { class: "column pending" },
      h("span", { class: "column-char" }, charLabel(character)),
      h("span", { class: "column-code" }, "000"),
      h("span", { class: "column-block" }, "000"))));
  previousBlocks = [];
  fill($("#encrypt-picker"));
  fill($("#encrypt-detail"), h("p", { class: "panel-text" }, message));
  fill($("#cipher-blocks"));
  fill($("#decrypt-picker"));
  fill($("#decrypt-detail"), h("p", { class: "panel-text" }, message));
  $("#error-cipher").textContent = "";
  fill($("#plaintext"));
  $("#toy-factor").textContent = message;
  $("#toy-pattern").textContent = message;
}

function renderHero(encrypted) {
  const chars = encrypted.chars;
  state.encIndex = Math.min(state.encIndex, Math.max(chars.length - 1, 0));
  const columns = chars.map((c, index) => {
    const fresh = previousBlocks[index] !== c.block;
    const digits = Array.from(c.block).map((digit, d) => h("span", { class: "digit", style: `--d:${d}` }, digit));
    return h("button", {
      type: "button",
      class: `column${c.fits ? "" : " too-big"}${fresh ? " fresh" : ""}`,
      style: `--col:${index}`,
      "aria-pressed": String(index === state.encIndex),
      "aria-label": `${charName(c.char)}, code ${c.code}, encrypts to ${c.block}${c.fits ? "" : ", too large for N"}`,
      onclick: () => {
        state.encIndex = index;
        render();
        $("#encrypt-detail").scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "center" });
      },
    },
    h("span", { class: "column-char", "aria-hidden": "true" }, charLabel(c.char)),
    h("span", { class: "column-code", "aria-hidden": "true" }, String(c.code)),
    h("span", { class: "column-block", "aria-hidden": "true" }, digits));
  });
  fill($("#hero-strip"), ...columns);
  previousBlocks = chars.map((c) => c.block);
  setTimeout(() => document.querySelectorAll(".column.fresh").forEach((el) => el.classList.remove("fresh")), 1600);
}

function picker(container, items, selected, onSelect) {
  fill(container, ...items.map((item, index) =>
    h("button", {
      type: "button",
      class: `pick${item.warn ? " too-big" : ""}`,
      "aria-pressed": String(index === selected),
      "aria-label": item.label,
      onclick: () => onSelect(index),
    },
    h("span", { class: "pick-char", "aria-hidden": "true" }, item.char),
    h("span", { class: "pick-num", "aria-hidden": "true" }, item.num))));
}

function bitsOf(value) {
  return h("span", { class: "bits", "aria-hidden": "true" },
    Array.from(value.toString(2)).map((bit) => h("span", { class: `bit${bit === "1" ? " on" : ""}` }, bit)));
}

function ladderTable(ladder, symbol, base, privateKey) {
  const rows = ladder.map((row, index) => {
    const calc = index === 0
      ? `${base} = ${row.square}`
      : `${ladder[index - 1].value}² = ${row.square}`;
    return h("tr", { class: row.used ? "used" : "unused" },
      h("td", {}, h("span", {}, base, h("sup", {}, String(row.power)))),
      h("td", {}, calc),
      h("td", {}, row.value),
      h("td", {}, row.used ? "1" : "0"));
  });
  return h("div", { class: "table-wrap" },
    h("table", { class: `data-table${privateKey ? " private" : ""}` },
      h("caption", { class: "visually-hidden" }, `Square-and-multiply rows for exponent ${symbol}`),
      h("thead", {}, h("tr", {},
        h("th", { scope: "col" }, "Power"),
        h("th", { scope: "col" }, "Calculation"),
        h("th", { scope: "col" }, "mod N"),
        h("th", { scope: "col" }, `Bit of ${symbol}`))),
      h("tbody", {}, rows)));
}

function multiplyLine(ladder, product, n) {
  const used = ladder.filter((row) => row.used).map((row) => row.value);
  return [
    "Multiply the rows whose bit is 1: ",
    num(used.join(" × ")),
    used.length > 1 ? [" = ", bigNum(product)] : "",
    ". Then ", bigNum(product), num(` mod ${n} = `),
  ];
}

function renderEncrypt(encrypted) {
  const { chars, keys: key } = encrypted;
  picker($("#encrypt-picker"), chars.map((c) => ({
    char: charLabel(c.char),
    num: c.block,
    warn: !c.fits,
    label: `${charName(c.char)} encrypts to ${c.block}`,
  })), state.encIndex, (index) => { state.encIndex = index; render(); });

  const detail = $("#encrypt-detail");
  if (!chars.length) {
    fill(detail, h("p", { class: "panel-text" }, "Type a message to see how each character is encrypted."));
  } else {
    const c = chars[state.encIndex];
    const code = Number(c.block);
    fill(detail,
      h("div", { class: "detail-head" },
        h("span", { class: "detail-char", "aria-hidden": "true" }, charLabel(c.char)),
        h("p", { class: "detail-summary" },
          `${charName(c.char)} has code M = `, num(c.code), ". E = ", pub(key.e), " is ", bitsOf(key.e),
          ` in binary. Each row below uses one bit, starting from the rightmost.`)),
      ladderTable(c.ladder, "E", "M", false),
      h("p", { class: "result-line" },
        multiplyLine(c.ladder, c.product, key.n), pub(code),
        c.block.length > String(code).length ? [", written as ", pub(c.block), ` so every block has ${key.width} digits.`] : "."),
      c.fits ? null : h("p", { class: "step-note warning" },
        `Code ${c.code} isn't below N = ${key.n}, so this block won't decrypt back to ${quoted(c.char)}.`));
  }

  const blocks = $("#cipher-blocks");
  fill(blocks, ...chars.map((c) => h("span", { class: c.fits ? null : "too-big" }, c.block)));
  $("#copy-cipher").dataset.value = encrypted.ciphertext;
  $("#copy-cipher").hidden = !encrypted.ciphertext;
}

function renderDecrypt(decrypted, encrypted) {
  const useButton = $("#use-cipher");
  useButton.hidden = !(state.cipherEdited && state.cipher !== encrypted.ciphertext);
  $("#error-cipher").textContent = decrypted.error || "";

  const blocks = decrypted.blocks || [];
  state.decIndex = Math.min(state.decIndex, Math.max(blocks.length - 1, 0));
  picker($("#decrypt-picker"), blocks.map((b) => ({
    char: b.char === null ? "?" : charLabel(b.char),
    num: b.block,
    warn: !b.fits || b.char === null,
    label: `Block ${b.block} decrypts to ${b.char === null ? "no valid character" : charName(b.char)}`,
  })), state.decIndex, (index) => { state.decIndex = index; render(); });

  const key = decrypted.keys;
  const detail = $("#decrypt-detail");
  if (decrypted.error) {
    fill(detail);
  } else if (!blocks.length) {
    fill(detail, h("p", { class: "panel-text" }, "Enter a ciphertext to decrypt it block by block."));
  } else {
    const b = blocks[state.decIndex];
    fill(detail,
      h("div", { class: "detail-head" },
        h("span", { class: "detail-char", "aria-hidden": "true" }, b.char === null ? "?" : charLabel(b.char)),
        h("p", { class: "detail-summary" },
          "Block ", pub(b.block), " is C = ", num(b.value), ". D = ", priv(key.d), " is ",
          h("span", { class: "private-bits" }, bitsOf(key.d)),
          ` in binary. Each row below uses one bit, starting from the rightmost.`)),
      ladderTable(b.ladder, "D", "C", true),
      h("p", { class: "result-line" },
        multiplyLine(b.ladder, b.product, key.n), priv(b.code),
        b.char === null
          ? ", which isn't a valid character code."
          : [", the code for ", h("strong", { class: "is-private" }, quoted(b.char)), "."]),
      b.fits ? null : h("p", { class: "step-note warning" },
        `This block isn't below N = ${key.n}, so encryption could never have produced it.`));
  }

  const plaintext = $("#plaintext");
  if (decrypted.error || !blocks.length) {
    fill(plaintext);
  } else if (decrypted.plaintext === null) {
    fill(plaintext, "Some blocks don't decrypt to valid characters.");
  } else {
    const matches = decrypted.plaintext === state.message.slice(0, 60);
    fill(plaintext,
      "Decrypted message: ", h("strong", {}, visible(decrypted.plaintext)),
      h("span", { class: `match${matches ? "" : " mismatch"}` }, matches ? "Matches your message" : "Differs from your message"));
  }
}

function renderToy(cracked, encrypted) {
  const key = cracked.keys;
  fill($("#toy-factor"),
    "Your public key is N = ", pub(key.n), " and E = ", pub(key.e), ". Trying divisors of N finds ",
    num(cracked.factor), ` after ${cracked.tries.toLocaleString()} ${cracked.tries === 1 ? "try" : "tries"}, so N = `,
    num(`${cracked.factor} × ${cracked.other}`), ". That gives φ(N) = ", priv(cracked.phi),
    " and, with step 2's algorithm, D = ", priv(cracked.d), ".");

  const counts = new Map();
  for (const c of encrypted.chars) {
    const entry = counts.get(c.char) || { count: 0, block: c.block };
    entry.count += 1;
    counts.set(c.char, entry);
  }
  const repeated = [...counts.entries()].find(([, info]) => info.count > 1);
  fill($("#toy-pattern"), ...(repeated
    ? [`${charName(repeated[0])} appears ${repeated[1].count} times in your message and becomes `,
      pub(repeated[1].block),
      " every time. Someone watching can spot repeated letters, and guess common ones, without any key."]
    : ["Every character in your message is different. Add a repeated letter, as in “hello”, and the same block shows up twice."]));
}

setupTheme();
setupInputs();
render();
startPython();
