(function () {
  "use strict";

  // --------- input collection -----------------------------------------------
  function collect(form) {
    const data = {};
    for (const el of form.elements) {
      if (!el.name) continue;
      data[el.name] = el.type === "checkbox" ? el.checked : el.value;
    }
    return data;
  }

  // --------- result rendering -----------------------------------------------
  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function renderTable(table) {
    const head =
      "<thead><tr>" +
      table.columns.map((c) => "<th>" + escapeHtml(c) + "</th>").join("") +
      "</tr></thead>";
    const body =
      "<tbody>" +
      table.rows
        .map(
          (row) =>
            "<tr>" +
            row.map((c) => "<td>" + escapeHtml(c) + "</td>").join("") +
            "</tr>"
        )
        .join("") +
      "</tbody>";
    return '<table class="out__table">' + head + body + "</table>";
  }

  // Tiny markdown renderer: headings, bold, italic, inline code, code fences,
  // links, paragraphs, lists. Keeps zero deps.
  function renderMarkdown(src) {
    const lines = src.replace(/\r\n/g, "\n").split("\n");
    const html = [];
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];

      if (line.startsWith("```")) {
        const buf = [];
        i++;
        while (i < lines.length && !lines[i].startsWith("```")) {
          buf.push(lines[i]);
          i++;
        }
        i++;
        html.push("<pre><code>" + escapeHtml(buf.join("\n")) + "</code></pre>");
        continue;
      }

      const heading = line.match(/^(#{1,6})\s+(.*)$/);
      if (heading) {
        const level = heading[1].length;
        html.push("<h" + level + ">" + inline(heading[2]) + "</h" + level + ">");
        i++;
        continue;
      }

      if (/^\s*[-*]\s+/.test(line)) {
        const items = [];
        while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
          items.push("<li>" + inline(lines[i].replace(/^\s*[-*]\s+/, "")) + "</li>");
          i++;
        }
        html.push("<ul>" + items.join("") + "</ul>");
        continue;
      }

      if (line.trim() === "") {
        i++;
        continue;
      }

      // paragraph: collect until blank line
      const buf = [line];
      i++;
      while (i < lines.length && lines[i].trim() !== "" && !/^(#{1,6})\s|^```|^\s*[-*]\s/.test(lines[i])) {
        buf.push(lines[i]);
        i++;
      }
      html.push("<p>" + inline(buf.join(" ")) + "</p>");
    }
    return html.join("\n");
  }

  function inline(s) {
    s = escapeHtml(s);
    s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    return s;
  }

  function renderBlock(block) {
    const wrap = document.createElement("div");
    switch (block.kind) {
      case "text":
        wrap.innerHTML = '<pre class="out__pre">' + escapeHtml(block.value) + "</pre>";
        break;
      case "json":
        wrap.innerHTML = '<pre class="out__pre out__pre--json">' + escapeHtml(block.value) + "</pre>";
        break;
      case "markdown":
        wrap.className = "out__md";
        wrap.innerHTML = renderMarkdown(block.value);
        break;
      case "html":
        wrap.className = "out__html";
        wrap.innerHTML = block.value;
        break;
      case "image":
        wrap.className = "out__image";
        wrap.innerHTML = '<img alt="" src="' + block.value.data_url + '">';
        break;
      case "table":
        wrap.className = "out__table-wrap";
        wrap.innerHTML = renderTable(block.value);
        break;
      case "file": {
        const v = block.value;
        if (v.is_image) {
          wrap.className = "out__image";
          wrap.innerHTML = '<img alt="' + escapeHtml(v.name) + '" src="' + v.data_url + '">';
        } else {
          wrap.className = "out__file";
          wrap.innerHTML =
            '<a download="' + escapeHtml(v.name) + '" href="' + v.data_url + '">' +
            escapeHtml(v.name) + " ↓</a>";
        }
        break;
      }
      default:
        wrap.innerHTML = '<pre class="out__pre">' + escapeHtml(String(block.value)) + "</pre>";
    }
    return wrap;
  }

  function setOutput(card, payload) {
    const out = card.querySelector(".out");
    const stdoutBlock = out.querySelector(".out__block--stdout");
    const stdoutPre = out.querySelector(".out__pre--stdout");
    const resultHost = out.querySelector(".out__result");

    out.hidden = false;
    resultHost.innerHTML = "";
    resultHost.classList.remove("out__result--err");

    if (payload.ok) {
      if (payload.stdout && payload.stdout.length) {
        stdoutPre.textContent = payload.stdout;
        stdoutBlock.hidden = false;
      } else {
        stdoutBlock.hidden = true;
      }
      resultHost.appendChild(renderBlock(payload.result));
    } else {
      stdoutBlock.hidden = true;
      resultHost.classList.add("out__result--err");
      const pre = document.createElement("pre");
      pre.className = "out__pre out__pre--err";
      pre.textContent = payload.error;
      resultHost.appendChild(pre);
    }
  }

  // --------- submit handling ------------------------------------------------
  async function runForm(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const card = form.closest(".card");
    const index = form.dataset.index;
    const button = form.querySelector("button[type=submit]");

    button.disabled = true;
    button.textContent = "Running…";

    try {
      const res = await fetch("/run/" + index, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(collect(form)),
      });
      const json = await res.json();
      setOutput(card, json);
    } catch (err) {
      setOutput(card, { ok: false, error: String(err) });
    } finally {
      button.disabled = false;
      button.textContent = "Run";
    }
  }

  document.querySelectorAll("form.card__form").forEach(function (form) {
    form.addEventListener("submit", runForm);
  });

  // --------- chat cards -----------------------------------------------------
  function initChat(root) {
    const index = root.dataset.index;
    const log = root.querySelector(".chat__log");
    const form = root.querySelector(".chat__form");
    const input = root.querySelector(".chat__input");
    const button = form.querySelector("button[type=submit]");
    const history = [];

    function autoresize() {
      input.style.height = "auto";
      input.style.height = Math.min(input.scrollHeight, 180) + "px";
    }
    input.addEventListener("input", autoresize);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        form.requestSubmit();
      }
    });

    function appendUser(text) {
      const wrap = document.createElement("div");
      wrap.className = "chat__msg chat__msg--user";
      const bubble = document.createElement("div");
      bubble.className = "chat__bubble";
      bubble.textContent = text;
      wrap.appendChild(bubble);
      log.appendChild(wrap);
      log.scrollTop = log.scrollHeight;
    }

    function appendBot(block, stdout) {
      const wrap = document.createElement("div");
      wrap.className = "chat__msg chat__msg--bot";
      const bubble = document.createElement("div");
      bubble.className = "chat__bubble";
      if (stdout && stdout.length) {
        const std = document.createElement("div");
        std.className = "chat__stdout";
        std.innerHTML =
          '<div class="chat__stdout-label">stdout</div><pre>' +
          escapeHtml(stdout) +
          "</pre>";
        bubble.appendChild(std);
      }
      bubble.appendChild(renderBlock(block));
      wrap.appendChild(bubble);
      log.appendChild(wrap);
      log.scrollTop = log.scrollHeight;
      return bubble;
    }

    function appendPending() {
      const wrap = document.createElement("div");
      wrap.className = "chat__msg chat__msg--bot chat__msg--pending";
      wrap.innerHTML = '<div class="chat__bubble"><span class="dots"><i></i><i></i><i></i></span></div>';
      log.appendChild(wrap);
      log.scrollTop = log.scrollHeight;
      return wrap;
    }

    function appendError(text) {
      const wrap = document.createElement("div");
      wrap.className = "chat__msg chat__msg--bot chat__msg--err";
      const bubble = document.createElement("div");
      bubble.className = "chat__bubble";
      bubble.textContent = text;
      wrap.appendChild(bubble);
      log.appendChild(wrap);
      log.scrollTop = log.scrollHeight;
    }

    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const message = input.value.trim();
      if (!message) return;

      appendUser(message);
      history.push({ role: "user", content: message });
      input.value = "";
      autoresize();
      input.disabled = true;
      button.disabled = true;
      const pending = appendPending();

      try {
        const res = await fetch("/chat/" + index, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: message, history: history.slice(0, -1) }),
        });
        const json = await res.json();
        pending.remove();
        if (json.ok) {
          appendBot(json.reply, json.stdout);
          const replyText =
            json.reply && typeof json.reply.value === "string"
              ? json.reply.value
              : "";
          history.push({ role: "assistant", content: replyText });
        } else {
          appendError(json.error);
        }
      } catch (err) {
        pending.remove();
        appendError(String(err));
      } finally {
        input.disabled = false;
        button.disabled = false;
        input.focus();
      }
    });
  }

  document.querySelectorAll(".chat").forEach(initChat);
})();
