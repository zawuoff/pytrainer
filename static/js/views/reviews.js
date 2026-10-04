import { api, esc, main, topicOf } from "../core.js";

/* ---------------------------------------------------------------- reviews */

export async function viewReviews() {
  const d = await api("reviews");
  main.innerHTML = `<div class="page narrow">
    <h1>Reviews</h1>
    <p class="dim" style="margin-top:10px;max-width:64ch">Steps you've solved come back just before you'd forget them, and each time you rebuild them from a blank file. A quick, clean rebuild pushes the next review far out; a struggle brings it back soon. That's how "I solved it once" becomes "I know it".</p>
    ${d.variants_on ? `<p class="faint small" style="max-width:64ch">Reviews marked <span class="pill">new form</span> test the same skill with new names and data, written by your AI connection. The rest are prepared in the background.</p>` : ""}
    <section class="section"><h2>Due now</h2>
      ${d.due.length ? `<ol class="steps">${d.due.map((r) => `<li><a href="#/step/${r.id}?review"><span>${esc(r.title)}<span class="sub">${esc(topicOf(r.topic)?.title || r.topic)}</span></span>
        <span class="kind">${r.variant ? `<span class="pill">new form</span> ` : ""}${r.lapses ? `<span class="pill fail">${r.lapses} lapse${r.lapses > 1 ? "s" : ""}</span>` : ""}</span><span class="dot attempted"></span></a></li>`).join("")}</ol>`
        : `<p class="dim">Nothing due. Solve new steps and they'll show up here later.</p>`}
    </section>
    ${d.upcoming.length ? `<section class="section"><h2>Coming up</h2><table class="ptable">${d.upcoming.map((u) => `<tr><td>${esc(u.title)}</td><td class="faint">${esc(u.next_review)}</td></tr>`).join("")}</table></section>` : ""}
  </div>`;
}
