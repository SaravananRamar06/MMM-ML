// Builds "Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx" (23 slides), applying the
// 9 Nov 2026 presentation audit (branch codex/presentation-audit, 118fdf5). The original deck is build_final.js.
// Run: NODE_PATH=<dir containing pptxgenjs> node build_final.js <dir containing scripts/apply_theme.js>
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(path.join(process.argv[2], "scripts/apply_theme.js"));

const A = (f) => path.join(__dirname, "..", "assets", f);
const OUT = path.join(__dirname, "..", "Final Presentation - Porosity in an AM Wing Bracket (corrected).pptx");

const THEME = {
  name: "Aero Bracket",
  headFontFace: "Arial",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0B2545", lt1: "FFFFFF", dk2: "134074", lt2: "EEF4FA",
    accent1: "F28C28", accent2: "13A4D8", accent3: "5C6B7A", accent4: "A9B8C6",
    accent5: "D9E6F2", accent6: "2BB673", hlink: "134074", folHlink: "5C6B7A",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.title = "Effect of Porosity on an Additively Manufactured Aircraft Wing Bracket";
pres.author = "Pranav Parasuram C, R Saravanan, Dinesh Y, Amit Narayan K";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const NAVY = C.text1, STEEL = C.text2, ORANGE = C.accent1, CYAN = C.accent2, MUTED = C.accent3,
  LINE = C.accent4, PALE = C.accent5, GREEN = C.accent6, ICE = C.background2, WHITE = C.background1;
const FOOT = "Effect of porosity on an AM aircraft wing bracket  ·  IIITDM Kancheepuram";

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "COVER",
  background: { path: A("bg_blueprint.png") },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 1.35, w: 7.6, h: 2.3, fontSize: 38, bold: true, color: WHITE, align: "left", valign: "bottom", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: WHITE },
  margin: [0.5, 0.6, 0.7, 0.6],
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.42, w: 5.8, h: 0.28, fontSize: 11, bold: true, color: ORANGE, charSpacing: 3, align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.78, w: 12.1, h: 0.7, fontSize: 30, bold: true, color: NAVY, align: "left", valign: "top", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: 0.6, y: 7.05, w: 9, h: 0.28, fontSize: 10, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: 12.23, y: 7.05, w: 0.5, h: 0.28, fontSize: 10, color: MUTED, align: "right", margin: 0 },
});
pres.defineSlideMaster({
  title: "DARK",
  background: { color: NAVY },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.42, w: 5.8, h: 0.28, fontSize: 11, bold: true, color: ORANGE, charSpacing: 3, align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.78, w: 12.1, h: 0.7, fontSize: 30, bold: true, color: WHITE, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.23, y: 7.05, w: 0.5, h: 0.28, fontSize: 10, color: LINE, align: "right", margin: 0 },
});

// ------------------------------------------------------------------ helpers
let n = 0;
const uid = (s) => `${s}_${++n}`;
const B = (t, o) => ({ text: t, options: Object.assign({ bold: true }, o) });
const R = (t, o) => ({ text: t, options: Object.assign({}, o) });
const sub = (t) => R(t, { subscript: true });
const sup = (t) => R(t, { superscript: true });

function text(s, t, o) {
  s.addText(t, Object.assign({ isTextBox: true, margin: 0, fontSize: 15, color: NAVY, valign: "top", objectName: uid("txt") }, o));
}
function card(s, x, y, w, h, fill, line) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: fill || ICE }, line: { color: line || fill || ICE, width: 1 }, objectName: uid("card") });
}
function dot(s, x, y, label, color, d) {
  d = d || 0.44;
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: color || NAVY }, line: { color: color || NAVY }, objectName: uid("dot") });
  s.addText(label, { x, y, w: d, h: d, isTextBox: true, margin: 0, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle", objectName: uid("dotlbl") });
}
function img(s, file, x, y, w, ratio, alt) {
  s.addImage({ path: A(file), x, y, w, h: w / ratio, altText: alt, objectName: uid("img") });
}
const STAGES = ["Problem", "CAD & Ansys", "EDA", "Model", "Evaluate", "Deploy"];
function tracker(s, active, dark) {
  const x0 = 6.95, step = 0.97;
  STAGES.forEach((st, i) => {
    const x = x0 + i * step, on = i === active;
    if (i < STAGES.length - 1) s.addShape(pres.shapes.LINE, { x: x + 0.15, y: 0.505, w: step - 0.15, h: 0, line: { color: dark ? STEEL : PALE, width: 1.25 }, objectName: uid("trk_line") });
    s.addShape(pres.shapes.OVAL, { x, y: 0.43, w: 0.15, h: 0.15, fill: { color: on ? ORANGE : (dark ? NAVY : WHITE) }, line: { color: on ? ORANGE : LINE, width: 1.25 }, objectName: uid("trk_dot") });
    text(s, st, { x: x - 0.3, y: 0.6, w: 0.92, h: 0.22, fontSize: 10, bold: on, color: on ? ORANGE : (dark ? LINE : MUTED), align: "left" });
  });
}
function content(section, stage, kicker, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(kicker.toUpperCase(), { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  if (stage !== null) tracker(s, stage, false);
  return s;
}
const AX = { catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 13, catAxisLabelFontFace: "+mn-lt", valAxisLabelColor: HEX.accent3, valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt", valGridLine: { color: HEX.accent5, size: 0.75 }, catGridLine: { style: "none" }, dataLabelFontSize: 13, dataLabelFontFace: "+mn-lt", dataLabelColor: HEX.dk1, titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: HEX.dk1 };

// ================================================================== 1 Cover
pres.addSection({ title: "Opening" });
{
  const s = pres.addSlide({ masterName: "COVER", sectionTitle: "Opening" });
  text(s, "MULTISCALE MODELLING OF MATERIALS USING MACHINE LEARNING  ·  COURSE PROJECT", { x: 0.7, y: 0.75, w: 8.5, h: 0.3, fontSize: 12, bold: true, color: ORANGE, charSpacing: 2 });
  s.addText("Effect of Porosity on an Additively Manufactured Aircraft Wing Bracket", { placeholder: "title" });
  text(s, "From AlSi10Mg material data to bracket stress, with a JC-backbone neural network (JC-PINN) and Ansys", { x: 0.7, y: 3.8, w: 7.4, h: 0.7, fontSize: 17, italic: true, color: LINE });
  const team = [["Pranav Parasuram C", "ME24B1061"], ["R Saravanan", "ME24I1006"], ["Dinesh Y", "ME24B1043"], ["Amit Narayan K", "ME24I1024"]];
  text(s, "TEAM", { x: 0.7, y: 4.75, w: 2, h: 0.25, fontSize: 11, bold: true, color: CYAN, charSpacing: 3 });
  team.forEach(([nm, roll], i) => {
    const x = 0.7 + (i % 2) * 3.4, y = 5.05 + Math.floor(i / 2) * 0.42;
    text(s, [B(nm, { color: WHITE }), R("   " + roll, { color: LINE, fontSize: 13 })], { x, y, w: 3.3, h: 0.36, fontSize: 16 });
  });
  text(s, [B("Course instructor  ", { color: CYAN }), R("Prof. Arul Kumar Mariyappan", { color: WHITE })], { x: 0.7, y: 6.05, w: 7.5, h: 0.32, fontSize: 15 });
  text(s, "Indian Institute of Information Technology, Design and Manufacturing (IIITDM) Kancheepuram", { x: 0.7, y: 6.45, w: 8.5, h: 0.32, fontSize: 14, color: LINE });
  s.addNotes("Good morning. We are presenting our course project on how porosity from 3D printing affects an aluminium aircraft wing bracket: a neural material model built on a Johnson-Cook backbone, which we call the JC-PINN, the team's Ansys bracket runs, and the fracture step we still plan to add.");
}

// ================================================================== 2 Problem statement
pres.addSection({ title: "Problem" });
{
  const s = content("Problem", 0, "01 · Problem statement", "Printed brackets are light, but they carry hidden pores");
  const pts = [
    [B("The part: "), R("an aircraft wing-rib bracket that carries load from the rib into the wing spar.")],
    [B("The process: "), R("laser powder-bed fusion (metal 3D printing) in AlSi10Mg aluminium alloy, for low weight and complex shapes.")],
    [B("The catch: "), R("printing traps gas pores and leaves lack-of-fusion voids. Some porosity is always present.")],
    [B("The risk: "), R("each pore is a ready-made flaw. Under repeated flight loads it can grow into the crack that breaks the bracket.")],
  ];
  pts.forEach((p, i) => {
    dot(s, 0.6, 1.85 + i * 0.95, String(i + 1), i === 3 ? ORANGE : NAVY);
    text(s, p, { x: 1.25, y: 1.85 + i * 0.95, w: 5.95, h: 0.85, fontSize: 16 });
  });
  card(s, 7.7, 1.8, 5.0, 3.55, ICE);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.1, y: 2.15, w: 4.2, h: 2.5, rectRadius: 0.06, fill: { color: LINE }, line: { color: NAVY, width: 1.25 }, objectName: "section_block" });
  const pores = [[8.45, 2.45, 0.22], [9.4, 3.0, 0.14], [10.3, 2.4, 0.3], [11.4, 2.75, 0.18], [8.8, 3.9, 0.26], [10.0, 3.65, 0.12], [11.0, 4.15, 0.22], [11.85, 3.7, 0.14], [9.75, 4.3, 0.16], [8.4, 3.25, 0.12], [11.8, 2.35, 0.1]];
  pores.forEach(([x, y, d], i) => s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d * (i % 3 === 0 ? 0.7 : 1), fill: { color: WHITE }, line: { color: NAVY, width: 0.75 }, objectName: uid("pore") }));
  s.addShape(pres.shapes.OVAL, { x: 10.3, y: 2.4, w: 0.3, h: 0.3, fill: { color: WHITE }, line: { color: ORANGE, width: 2.25 }, objectName: "pore_hl" });
  text(s, "Printed cross-section (schematic). Porosity φ = pore volume ÷ total volume.", { x: 8.1, y: 4.8, w: 4.2, h: 0.45, fontSize: 12, color: MUTED, align: "center" });
  card(s, 0.6, 5.85, 12.1, 0.95, NAVY);
  text(s, [R("Problem:  ", { color: ORANGE, bold: true }), R("how much does porosity reduce the size of flaw the bracket can safely carry, and how can a designer check that quickly?", { color: WHITE })], { x: 0.9, y: 5.98, w: 11.6, h: 0.7, fontSize: 18, valign: "middle" });
  s.addNotes("The bracket is printed, not machined, so it is light and can have an optimised shape. But printing always leaves pores. Each pore is a flaw already inside the part, and repeated flight loads can grow it into a crack. So our problem is: how much does porosity cut the flaw size the bracket can tolerate, and how can a designer check that quickly?");
}

// ================================================================== 3 Objective
{
  const s = content("Problem", 0, "02 · Objective", "Estimate the critical flaw size as porosity rises");
  const obj = [
    ["Learn the material", "Train a neural network on the 73 supplied AlSi10Mg simulations to predict the stress history within the sampled temperature, strain-rate, density, G and strain ranges. Sparse conditions need extra caution."],
    ["Load the bracket", "Pass those curves into Ansys and find the stress field around the bracket's critical location. This coupling is proposed, not yet validated."],
    ["Estimate the critical flaw size", [R("For a specified crack geometry and orientation, compute K"), sub("I"), R("(a) and solve K"), sub("I"), R("(a"), sub("c"), R(") = K"), sub("IC"), R(" across porosity. Planned.")]],
  ];
  obj.forEach(([h, b], i) => {
    const y = 1.8 + i * 1.3;
    card(s, 0.6, y, 6.7, 1.18, ICE);
    dot(s, 0.85, y + 0.35, String(i + 1), i === 2 ? ORANGE : STEEL, 0.48);
    text(s, h, { x: 1.55, y: y + 0.1, w: 5.6, h: 0.35, fontSize: 18, bold: true });
    text(s, b, { x: 1.55, y: y + 0.45, w: 5.6, h: 0.7, fontSize: 13.5, color: MUTED });
  });
  card(s, 7.7, 1.8, 5.0, 3.85, NAVY);
  text(s, "TARGET QUANTITY (PLANNED)", { x: 8.0, y: 1.98, w: 4.4, h: 0.26, fontSize: 11, bold: true, color: CYAN, charSpacing: 3 });
  text(s, [R("K"), sub("I"), R("(a"), sub("c"), R(")  =  K"), sub("IC")], { x: 8.0, y: 2.3, w: 4.5, h: 0.6, fontSize: 28, bold: true, color: WHITE });
  const terms = [
    ["a", "crack size for the chosen crack model (depth, radius or half-length); a CT pore needs a pore-to-crack convention", 3.0],
    ["K", [R("K"), sub("I"), R(" from a handbook solution or FE fracture analysis, using the stress that opens that crack, not peak von Mises")], 3.68],
    ["K", [R("K"), sub("IC"), R(": source and porosity dependence still to be defined (no toughness data supplied)")], 4.36],
  ];
  terms.forEach(([sy, d, y]) => {
    text(s, sy, { x: 8.0, y, w: 0.4, h: 0.4, fontSize: 17, bold: true, color: ORANGE });
    text(s, d, { x: 8.45, y: y + 0.02, w: 4.05, h: 0.64, fontSize: 12.5, color: WHITE });
  });
  text(s, [R("Simple Mode-I case: a"), sub("c"), R(" = (1/π)(K"), sub("IC"), R(" ⁄ Yσ)², σ = crack-opening stress. Check LEFM validity; use J if plasticity is significant.")], { x: 8.0, y: 5.02, w: 4.5, h: 0.55, fontSize: 11.5, color: LINE });
  text(s, [R("CL here is a "), B("static critical crack size"), R(": the largest crack of the specified type that does not fracture under the given load. It is not a fatigue-life or airworthiness criterion. Study point: porosity φ = 4 % (assumed; ρ = 2592 kg/m³).")],
    { x: 0.6, y: 5.85, w: 12.1, h: 0.85, fontSize: 15 });
  s.addNotes("We have three objectives. First, learn the material behaviour from the 73 supplied simulations with a neural network, within the ranges those simulations cover. Second, pass that behaviour into Ansys and find the stress around the bracket's critical location; that coupling is proposed, not yet validated. Third, and still planned: estimate the critical flaw size. That needs a specified crack geometry and orientation, a stress intensity K-one of a computed from a handbook solution or a finite-element fracture analysis using the stress that opens the crack, not the peak von Mises stress, and a toughness K-I-C we have not yet sourced. The familiar formula a-c equals one over pi times K-I-C over Y sigma squared is only the simple Mode-I special case. The result is a static critical crack size, not a fatigue or airworthiness criterion.");
}

// ================================================================== 4 Roadmap / life cycle
{
  const s = content("Problem", null, "03 · Our approach", "The data science life cycle we followed");
  const st = [
    ["Problem", "Porosity in a printed wing bracket; target CL(φ)", NAVY],
    ["CAD & Ansys", "Bracket geometry, loads, supports; 3 team Ansys runs", STEEL],
    ["EDA", "73 simulations explored: coverage, trends, key inputs", STEEL],
    ["Model", "JC-backbone hybrid (JC-PINN, λ = 0) selected and trained", CYAN],
    ["Evaluate", "Scored after locking on 37 held-out simulations", CYAN],
    ["Deploy", "Planned: a bracket-check concept", ORANGE],
  ];
  s.addShape(pres.shapes.LINE, { x: 1.2, y: 2.62, w: 10.9, h: 0, line: { color: PALE, width: 3 }, objectName: "life_line" });
  st.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 2.05;
    s.addShape(pres.shapes.OVAL, { x: x + 0.38, y: 2.2, w: 0.84, h: 0.84, fill: { color: col }, line: { color: WHITE, width: 3 }, objectName: uid("stage") });
    text(s, String(i + 1).padStart(2, "0"), { x: x + 0.38, y: 2.2, w: 0.84, h: 0.84, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle" });
    text(s, h, { x, y: 3.25, w: 1.9, h: 0.38, fontSize: 17, bold: true, align: "center", color: col });
    text(s, b, { x: x + 0.05, y: 3.68, w: 1.8, h: 1.1, fontSize: 13, color: MUTED, align: "center" });
  });
  card(s, 0.6, 5.0, 12.1, 1.75, ICE);
  text(s, "WHY IT IS MULTISCALE", { x: 0.9, y: 5.15, w: 4, h: 0.26, fontSize: 11, bold: true, color: STEEL, charSpacing: 3 });
  text(s, [B("Material scale: "), R("the network learns how the simulated AlSi10Mg stress varies with temperature, rate, density and G.   "), B("Part scale: "), R("the team's Ansys runs load the bracket; feeding our curves into Ansys is proposed.   "), B("Decision (planned): "), R("fracture mechanics with a specified crack model turns the local stress into a critical crack size.")],
    { x: 0.9, y: 5.47, w: 11.5, h: 1.2, fontSize: 15 });
  s.addNotes("This is the path through the talk, following the data science life cycle. The first five stages are done: the problem, the team's Ansys runs, the data exploration, the model and its evaluation. Deployment is planned, not built. The model is a Johnson-Cook-backbone hybrid; its selected physics-loss weight is zero. It is multiscale in intent: the network works at the material scale, Ansys at the part scale, and a fracture model would turn local stress into a critical crack size. The material-to-Ansys coupling and the fracture step are still proposed.");
}

// ================================================================== 5 CAD + loads + supports
pres.addSection({ title: "CAD and Ansys" });
{
  const s = content("CAD and Ansys", 1, "04 · CAD model, loads and supports", "Rib Bracket.STEP: geometry, loads and supports");
  img(s, "forces.png", 0.5, 1.7, 6.3, 1.5495, "Bracket planform with the bearing force F on the upper half of the bore, fixed supports on both mounting faces, reactions R and moment M = F × 210 mm");
  const rows = [
    ["Envelope", "231.5 × 230 × 40 mm plate"],
    ["Volume · mass", "778 cm³ · ≈ 2.1 kg at 2700 kg/m³"],
    ["Material", "AlSi10Mg, laser powder-bed fusion"],
    ["Load F", "Bearing load along +Y on the upper half of the Ø10 mm bore (628 mm²); magnitude and load history not archived"],
    ["Supports", "Fixed on both 50 × 40 mm spar mounting faces (team set-up; not verifiable from archived files)"],
    ["Reactions", "R = F, M = F × 210 mm (static-equilibrium idealisation)"],
    ["Load path", "Truss estimate: lower arm in tension, diagonal arm in compression"],
  ];
  s.addTable(rows.map(([k, v], i) => [
    { text: k, options: { bold: true, color: i === 3 ? ORANGE : NAVY, fontSize: 12.5, valign: "middle", fill: { color: i % 2 ? WHITE : ICE } } },
    { text: v, options: { color: NAVY, fontSize: 12.5, valign: "middle", fill: { color: i % 2 ? WHITE : ICE } } },
  ]), { x: 7.55, y: 1.7, w: 5.2, colW: [1.4, 3.8], rowH: [0.36, 0.36, 0.36, 0.62, 0.62, 0.42, 0.42], border: { type: "none" }, margin: [0.03, 0.1, 0.03, 0.1], fontFace: "Calibri", objectName: "cad_table" });
  img(s, "bore_compact.png", 8.25, 5.2, 4.0, 2.335, "Two bore close-ups: a load on the whole bore pulls the lower half into the hole; a pin load presses only on the upper half");
  card(s, 0.6, 5.95, 6.6, 0.9, ICE);
  text(s, [B("Why only the upper half? ", { color: ORANGE }), R("A pin can only push: it bears on the half of the bore the load drives it into, and the lower half opens a gap. Loading the whole bore would pull on the lower half and spread F over twice the area.")],
    { x: 0.8, y: 6.02, w: 6.25, h: 0.78, fontSize: 13, valign: "middle" });
  s.addNotes("This slide summarises the structural set-up. The geometry is measured from the STEP file: a 40 mm thick AlSi10Mg plate with two arms meeting at a 10 mm bore, 778 cubic centimetres, about 2.1 kg at 2700 kilograms per cubic metre. The pin load F acts upward on the upper half of the bore, because a pin can only push. The team describes both spar mounting faces as fixed; we could not verify the load magnitude, load history or supports from the archived files. R equals F and the moment F times 210 mm are static-equilibrium idealisations, and the tension and compression labels come from a simple truss estimate.");
}

// ================================================================== 6 Ansys set-up
{
  const s = content("CAD and Ansys", 1, "05 · Ansys simulations", "Three explicit Ansys simulations supplied by the team");
  text(s, [R("Workbench project "), B("Comparison Study - Final"), R(": three "), B("Explicit Dynamics (AUTODYN)"), R(" systems, each importing Rib Bracket.STEP, with different material cards. Identical load, mesh and supports could not be verified: the set-up files were not archived.")],
    { x: 0.6, y: 1.7, w: 12.1, h: 0.65, fontSize: 15.5 });
  const sims = [
    ["A · Elastic", "EL", "curve_el.png", "σ = E·ε", "Linear and never yields. Card: density, E, ν.", STEEL, "Schematic elastic stress-strain line"],
    ["B · Elasto-plastic JC", "JC-B", "curve_jcb.png", "σy = (A + B εpⁿ)(1 + C ln ε̇*)(1 − T*ᵐ)", "Ansys' built-in Johnson–Cook strength in equivalent plastic strain εp: hardening, strain-rate and temperature terms.", NAVY, "Schematic Johnson-Cook hardening curves"],
    ["C · User-defined JC", "JC-U", "curve_jcu.png", "team's (εp, σy) table", "Multilinear hardening entered by the team; its source is unconfirmed. Ansys tables use εp, but our data and JC-PINN use total axial strain E11, so conversion needs a confirmed E.", ORANGE, "Schematic of tabular (plastic strain, yield stress) rows; the team's values are not archived"],
  ];
  sims.forEach(([h, code, file, f, b, col, alt], k) => {
    const x = 0.6 + k * 4.12, w = 3.85;
    card(s, x, 2.5, w, 4.35, ICE);
    text(s, [B(code + "  ", { color: col }), R(h, { color: NAVY, bold: true })], { x: x + 0.2, y: 2.6, w: w - 0.4, h: 0.38, fontSize: 16 });
    img(s, file, x + 0.55, 3.02, w - 1.1, 1.3206, alt);
    text(s, f, { x: x + 0.2, y: 5.06, w: w - 0.4, h: 0.33, fontSize: 13, bold: true, color: col === NAVY ? STEEL : col });
    text(s, b, { x: x + 0.2, y: 5.4, w: w - 0.4, h: 1.4, fontSize: 12.5, color: NAVY });
  });
  s.addNotes("The team ran three explicit dynamics systems in Ansys. Each imports the same bracket STEP file and uses a different material card. We could not confirm from the archived project that the load, mesh and supports are identical, because the set-up folder was not supplied. A is purely elastic. B uses Ansys' built-in Johnson-Cook strength, which is written in equivalent plastic strain. C is a multilinear hardening table entered by the team; where its numbers came from is unconfirmed. Note that an Ansys table expects plastic strain, while our data and our model use total axial strain, E11, so converting them would need a confirmed Young's modulus. The picture for C is only a schematic of table rows, not our curve.");
}

// ================================================================== 7 Ansys results
{
  const s = content("CAD and Ansys", 1, "06 · Ansys results", "Equivalent stress at t = 0.06 s");
  const sims = [
    ["EL", "Elastic", STEEL, "result_el.png", 1.3701, "595.27", "at the fixed corner of the upper mounting face (possible constraint singularity)"],
    ["JC-B", "Elasto-plastic JC", NAVY, "result_jcb.png", 1.3701, "320.79", "around the bore, where the load enters"],
    ["JC-U", "User-defined JC", ORANGE, "result_jcu.png", 1.3876, "323.81", "around the bore, where the load enters"],
  ];
  sims.forEach(([c, nme, col, file, ratio, mx, where], k) => {
    const x = 0.6 + k * 4.12, w = 3.85;
    card(s, x, 1.7, w, 4.85, ICE);
    text(s, [B(c + "  ", { color: col }), R(nme, { color: MUTED })], { x: x + 0.2, y: 1.82, w: w - 0.4, h: 0.38, fontSize: 17 });
    img(s, file, x + 0.15, 2.3, w - 0.3, ratio, `${nme}: von Mises stress contour at 0.06 s, maximum ${mx} MPa (team screenshot)`);
    text(s, "peak von Mises stress", { x: x + 0.2, y: 5.0, w: w - 0.4, h: 0.28, fontSize: 12.5, color: MUTED });
    text(s, [B(mx, { color: col === NAVY ? STEEL : col }), R(" MPa", { color: NAVY, fontSize: 17 })], { x: x + 0.2, y: 5.25, w: w - 0.4, h: 0.6, fontSize: 32 });
    text(s, where, { x: x + 0.2, y: 5.88, w: w - 0.4, h: 0.62, fontSize: 13.5 });
  });
  text(s, "Ansys contours supplied by the team (Ansys reports MPa). Load history, mesh convergence, energy balance and material-card provenance are not verified from the archived set-up.", { x: 0.6, y: 6.6, w: 12.1, h: 0.4, fontSize: 11.5, color: MUTED });
  s.addNotes("These are the team's von Mises stress contours, all at 0.06 seconds; they are screenshot results, not re-run by us. The colour scales differ, so read the legend numbers. The elastic run peaks at 595.27 megapascals at the fixed corner of the upper mounting face; a peak at a fixed corner can be a constraint singularity that grows with mesh refinement. Both Johnson-Cook runs peak at about 321 to 324 megapascals around the bore. We could not check load history, mesh convergence or energy balance, because the set-up files were not archived.");
}

// ================================================================== 8 Ansys comparison
{
  const s = content("CAD and Ansys", 1, "07 · Ansys comparison", "The supplied JC runs have similar peak stresses at 0.06 s");
  s.addChart(pres.charts.BAR, [{ name: "Peak von Mises stress (MPa)", labels: ["EL", "JC-B", "JC-U"], values: [595.27, 320.79, 323.81] }], Object.assign({}, AX, {
    x: 0.6, y: 1.7, w: 5.6, h: 4.45, barDir: "col", barGapWidthPct: 70, chartColors: [HEX.dk2, HEX.dk1, HEX.accent1], showLegend: false,
    showTitle: true, title: "Peak von Mises stress at t = 0.06 s (MPa, team screenshots)", showValue: true, dataLabelPosition: "outEnd", dataLabelFontBold: true, dataLabelFormatCode: "0.0",
    catAxisLabelFontBold: true, valAxisMinVal: 0, valAxisMaxVal: 700, valAxisMajorUnit: 100, objectName: "peak_chart",
  }));
  const finds = [
    ["1.86×", "Elastic peak vs built-in JC", "595.27 vs 320.79: plasticity lowers the peak by about 46 %. The elastic peak sits at a fixed corner and may be mesh-dependent.", STEEL],
    ["0.94 %", "JC-U peak vs built-in JC", "323.81 vs 320.79. One peak at one instant does not validate the material law, the full response or JC-PINN-to-Ansys coupling.", ORANGE],
    ["Bore", "Plastic-run peaks sit at the bore", "Where the pin load enters. A fracture check would need the crack-opening stress there, not the peak von Mises value.", NAVY],
  ];
  finds.forEach(([big, h, b, col], i) => {
    const y = 1.7 + i * 1.5;
    card(s, 6.6, y, 6.1, 1.38, ICE);
    text(s, big, { x: 6.8, y: y + 0.2, w: 1.7, h: 0.95, fontSize: 30, bold: true, color: col === NAVY ? STEEL : col, valign: "middle" });
    text(s, h, { x: 8.55, y: y + 0.12, w: 4.0, h: 0.36, fontSize: 16.5, bold: true });
    text(s, b, { x: 8.55, y: y + 0.5, w: 4.0, h: 0.85, fontSize: 13, color: MUTED });
  });
  text(s, "JC-U is the proposed route for our material curves into Ansys; the table's provenance and full response remain to be checked.", { x: 0.6, y: 6.25, w: 12.1, h: 0.35, fontSize: 15, bold: true, color: ORANGE });
  text(s, "Ansys contours supplied by the team; not independently re-run. Set-up (load, mesh, energy balance) not archived.", { x: 0.6, y: 6.68, w: 12.1, h: 0.28, fontSize: 11, color: MUTED });
  s.addNotes("Three observations from the team's screenshots. The elastic run's peak is 1.86 times the built-in Johnson-Cook peak, 595.27 against 320.79; plasticity lowers the peak by about 46 percent. That elastic peak sits at a fixed corner, which may be a mesh-dependent singularity. The user-defined run's peak differs from the built-in one by 0.94 percent. That is a single number at a single instant: it does not validate the material law, the full response, or any coupling from our model to Ansys, and we do not know where the user-defined table came from. In the plastic runs the peak sits at the bore. For a fracture check we would need the stress that opens a specified crack there, not the peak von Mises value.");
}

// ================================================================== 9 EDA: dataset
pres.addSection({ title: "EDA" });
{
  const s = content("EDA", 2, "08 · Exploratory data analysis", "The data: 73 AlSi10Mg simulations from the professor");
  const stats = [["108", "planned simulations"], ["73", "with results"], ["2.2 M", "rows of history"], ["5 → 1", "inputs → output"]];
  stats.forEach(([v, l], i) => {
    const x = 0.6 + i * 1.6;
    text(s, v, { x, y: 1.75, w: 1.55, h: 0.7, fontSize: 30, bold: true, color: i === 1 ? ORANGE : NAVY });
    text(s, l, { x, y: 2.45, w: 1.5, h: 0.5, fontSize: 13, color: MUTED });
  });
  const hdr = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: STEEL }, align: "center", valign: "middle", fontSize: 13 } });
  const cell = (v) => ({ text: String(v), options: { align: "center", valign: "middle", fontSize: 15, bold: true, color: v === 0 ? MUTED : (v === 1 ? WHITE : NAVY), fill: { color: v === 0 ? WHITE : (v === 1 ? ORANGE : (v === 9 ? PALE : ICE)) } } });
  const lab = (t) => ({ text: t, options: { bold: true, align: "left", valign: "middle", fontSize: 13, color: NAVY, fill: { color: WHITE } } });
  s.addTable([
    [{ text: "cases available", options: { fontSize: 12, color: MUTED, fill: { color: WHITE } } }, hdr("10⁻⁵ /s"), hdr("10⁻⁴ /s"), hdr("10⁻³ /s")],
    [lab("30 °C"), cell(9), cell(9), cell(9)],
    [lab("100 °C"), cell(9), cell(9), cell(9)],
    [lab("200 °C"), cell(1), cell(9), cell(9)],
    [lab("300 °C"), cell(0), cell(0), cell(0)],
  ], { x: 0.6, y: 3.2, w: 6.3, colW: [1.65, 1.55, 1.55, 1.55], rowH: 0.48, border: { type: "solid", pt: 1, color: "FFFFFF" }, fontFace: "Calibri", objectName: "coverage_table" });
  text(s, "Each cell holds 9 combinations of density × shear modulus. Only one case at 200 °C, 10⁻⁵ /s; none at 300 °C.", { x: 0.6, y: 5.75, w: 6.3, h: 0.6, fontSize: 13, color: MUTED });
  card(s, 7.35, 1.75, 5.35, 5.0, ICE);
  text(s, "WHAT EACH SIMULATION GIVES", { x: 7.6, y: 1.95, w: 4.9, h: 0.26, fontSize: 11, bold: true, color: STEEL, charSpacing: 3 });
  const vars = [
    ["Temperature T", "30 · 100 · 200 °C"],
    ["Strain rate ε̇", "10⁻⁵ · 10⁻⁴ · 10⁻³ /s"],
    ["Density ρ", "2488 · 2619 · 2700 kg/m³ → porosity via φ = 1 − ρ/2700 (confirmed by the user): 7.85 · 3 · 0 %. Physical interpretation pending the professor's confirmation"],
    ["Shear modulus G", "23 314 · 24 541 · 25 300 MPa"],
    ["Output", "von Mises stress Svm along axial strain E11 = 0–10 %"],
  ];
  const ys = [2.3, 2.92, 3.54, 4.72, 5.36];
  vars.forEach(([k, v], i) => {
    const y = ys[i];
    text(s, k, { x: 7.6, y, w: 4.9, h: 0.3, fontSize: 15, bold: true, color: i === 4 ? ORANGE : NAVY });
    text(s, v, { x: 7.6, y: y + 0.31, w: 4.9, h: i === 2 ? 0.68 : 0.34, fontSize: 13.5, color: MUTED });
  });
  text(s, "Units (°C, /s, kg/m³, MPa) confirmed by the user; no documentation of the generator was seen.", { x: 7.6, y: 6.2, w: 4.9, h: 0.48, fontSize: 11.5, color: STEEL, bold: true });
  s.addNotes("The professor gave us a design matrix of 108 simulations; 73 have results, about 2.2 million rows of history. Every cell of temperature and strain rate has 9 combinations of density and shear modulus, except 200 degrees at the slowest rate, which has only one case, and 300 degrees, which has none. Porosity is represented through density with the user-confirmed mapping, phi equals one minus rho over 2700: that gives 0, 3 and 7.85 percent for the three density levels, and our 4 percent study point corresponds to 2592. Whether density really encodes porosity in this dataset still needs the professor's confirmation.");
}

// ================================================================== 10 EDA: curves and factor effects
{
  const s = content("EDA", 2, "09 · Exploratory data analysis", "Temperature and strain rate drive the curves");
  img(s, "eda_curves.png", 0.45, 1.65, 7.9, 2.5581, "All 73 stress-strain curves coloured by temperature, and the strain-rate effect at 30 °C");
  const obs = [
    [B("Every curve ends below its starting stress: "), R("on average 138 → 68 (MPa) over 10 % strain.")],
    [B("Hotter means weaker; "), R("a faster rate starts higher but softens faster, so curves cross near 6 % strain.")],
    [B("Case 60 is irregular "), R("and the only case at 200 °C, 10⁻⁵ /s. We kept it.")],
  ];
  obs.forEach((p, i) => {
    dot(s, 0.6, 4.95 + i * 0.66, String(i + 1), i === 2 ? ORANGE : STEEL, 0.38);
    text(s, p, { x: 1.15, y: 4.97 + i * 0.66, w: 7.1, h: 0.6, fontSize: 14 });
  });
  s.addChart(pres.charts.BAR, [{ name: "Largest stress change (MPa)", labels: ["Temperature", "Strain rate", "Shear modulus G", "Density ρ"], values: [22.12, 17.45, 3.40, 0.19] }], Object.assign({}, AX, {
    x: 8.6, y: 1.7, w: 4.15, h: 4.55, barDir: "bar", barGapWidthPct: 55, chartColors: [HEX.accent1, HEX.dk2, HEX.accent2, HEX.accent4], showLegend: false,
    showTitle: true, title: "Stress change for one level step (MPa)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelFontBold: true,
    valAxisHidden: true, valGridLine: { style: "none" }, catAxisOrientation: "maxMin", valAxisMaxVal: 28, objectName: "factor_chart",
  }));
  text(s, "Mean of the largest gap between paired curves that differ in one input by one level. Stress in MPa (units confirmed by the user; no generator documentation).", { x: 8.6, y: 6.3, w: 4.15, h: 0.65, fontSize: 11, color: MUTED });
  s.addNotes("Left: all 73 curves. Every curve ends below where it starts, and hotter cases sit lower; that does not mean every step of every curve falls, the irregular case 60 included. Right: at 30 degrees, a faster rate starts higher but softens faster, so the curves cross. The chart compares pairs of cases that differ in one input only: one temperature step moves the curve by 22 megapascals, one rate step by 17, shear modulus by 3, and density by only 0.2. So this data says very little about porosity directly; that becomes important for the model.");
}

// ================================================================== 11 Data preparation
{
  const s = content("EDA", 2, "10 · Preparing the data", "From raw histories to a case-wise train-test split");
  const steps = [
    ["Resample", "Every curve is interpolated to the same 120 strain points (0.02–9.99 %), so slow cases with 100 000 rows don't outweigh fast ones with 1 000."],
    ["Split by case", "Random 50/50 split of whole simulations, as the professor asked: 36 for training, 37 held out from fitting (seed 42)."],
    ["Scale", "Scaler statistics are fitted only on the 36 training cases. (The test cases were explored in earlier project stages.)"],
    ["Learn", "Each query is (T, log ε̇, ρ, G, E11) → Svm: 36 × 120 = 4 320 training points from 36 independent simulations."],
  ];
  steps.forEach(([h, b], i) => {
    const y = 1.75 + i * 1.22;
    dot(s, 0.6, y + 0.1, String(i + 1), i === 1 ? ORANGE : STEEL, 0.5);
    if (i < steps.length - 1) s.addShape(pres.shapes.LINE, { x: 0.85, y: y + 0.65, w: 0, h: 0.62, line: { color: PALE, width: 2 }, objectName: uid("flow") });
    text(s, h, { x: 1.35, y: y + 0.05, w: 6.3, h: 0.38, fontSize: 18, bold: true });
    text(s, b, { x: 1.35, y: y + 0.45, w: 6.3, h: 0.7, fontSize: 14, color: MUTED });
  });
  s.addChart(pres.charts.DOUGHNUT, [{ name: "Split", labels: ["Training cases", "Held-out test cases"], values: [36, 37] }], {
    x: 8.2, y: 1.7, w: 4.4, h: 3.9, holeSize: 62, chartColors: [HEX.dk2, HEX.accent1], showLegend: true, legendPos: "b", legendFontSize: 13, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    showValue: true, showPercent: false, dataLabelColor: HEX.lt1, dataLabelFontSize: 16, dataLabelFontBold: true, dataLabelFontFace: "+mn-lt",
    showTitle: true, title: "73 simulations, split by case", titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: HEX.dk1, objectName: "split_chart",
  });
  card(s, 8.2, 5.85, 4.5, 0.95, ICE);
  text(s, "All 120 points of a simulation stay on the same side of the split.", { x: 8.4, y: 5.95, w: 4.1, h: 0.75, fontSize: 14, bold: true, color: STEEL, valign: "middle" });
  s.addNotes("Before modelling, we resample every curve to 120 strain points so that each simulation counts equally. We split whole simulations, not rows, 36 for training and 37 held out from fitting, as the professor asked. Scaler statistics come from the training cases only, although the test cases had been explored in earlier project stages. That leaves 4,320 training points, but they come from just 36 independent simulations, which we keep in mind when judging accuracy.");
}

// ================================================================== 12 Choosing the NN
pres.addSection({ title: "Model" });
{
  const s = content("Model", 3, "11 · Choosing the neural network", "Choosing the model: a JC-backbone hybrid");
  s.addChart(pres.charts.BAR, [
    { name: "Case cross-validation (training partition)", labels: ["JC equation alone", "Plain MLP", "JC-PINN (λ = 0)"], values: [10.238, 2.174, 2.098] },
    { name: "Unseen temperature–rate groups (used in selection)", labels: ["JC equation alone", "Plain MLP", "JC-PINN (λ = 0)"], values: [13.947, 11.900, 6.2349] },
  ], Object.assign({}, AX, {
    x: 0.6, y: 1.7, w: 7.0, h: 3.85, barDir: "col", barGapWidthPct: 60, chartColors: [HEX.accent4, HEX.accent1], showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    showTitle: true, title: "Mean curve RMSE, training side only (MPa, lower is better)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelFontSize: 12,
    valAxisMinVal: 0, valAxisMaxVal: 16, valAxisMajorUnit: 4, catAxisLabelFontSize: 13, objectName: "model_choice_chart",
  }));
  const opts = [
    ["JC equation alone", "Readable but too rigid: case-CV 10.24, groups 13.95.", MUTED],
    ["Plain MLP", "Case-CV 2.17, but 11.90 on unseen temperature–rate groups.", STEEL],
    ["JC-PINN (selected)", "JC equation × learned correction. Physics-loss weight λ = 0: seven JC constants and the correction are fitted jointly to data.", ORANGE],
  ];
  opts.forEach(([h, b, col], i) => {
    const y = 1.7 + i * 1.3;
    card(s, 7.95, y, 4.75, 1.18, i === 2 ? NAVY : ICE);
    text(s, h, { x: 8.15, y: y + 0.1, w: 4.4, h: 0.34, fontSize: 16.5, bold: true, color: i === 2 ? ORANGE : col === MUTED ? NAVY : col });
    text(s, b, { x: 8.15, y: y + 0.44, w: 4.4, h: 0.72, fontSize: 13, color: i === 2 ? WHITE : MUTED });
  });
  card(s, 0.6, 5.68, 12.1, 0.78, PALE);
  text(s, [B("No accuracy benefit from physics is shown. ", { color: ORANGE }), R("The same network with the JC equation switched off scored better (groups 5.63 vs 6.23; test 0.338 vs 0.439). We keep the JC backbone as the project's adopted governing form; its constants are fitted jointly with the correction, not independent material properties.")],
    { x: 0.8, y: 5.72, w: 11.75, h: 0.7, fontSize: 13.5, valign: "middle" });
  text(s, "Group scores were used to select among 14 JC-PINN settings, and the MLP's setting was nested in its group test, so they are not independent estimates of superiority; optimism is not quantified. Curve RMSE in MPa.",
    { x: 0.6, y: 6.52, w: 12.1, h: 0.45, fontSize: 11, color: MUTED });
  s.addNotes("We compared approaches using only the training partition. The first bar of each pair is case cross-validation on training cases; the second is the mean over nine hidden temperature-rate groups. The JC equation alone is readable but too rigid. A plain MLP scores 2.17 in cross-validation but 11.90 on hidden groups. The selected JC-PINN, the JC equation times a learned correction, scores 2.10 and 6.23. Two things must be said plainly. First, the selected setting has physics-loss weight zero: no physics residual penalty is active; the seven JC constants and the correction are fitted jointly to data. Second, the same network with the equation switched off scored better, 5.63 against 6.23 on groups and 0.338 against 0.439 on test, so these comparisons show no accuracy benefit from the physics. We keep the backbone because the project adopted that governing form. The group scores were also used in selection, so they are not independent evidence that one model is better.");
}

// ================================================================== 13 JC-PINN versus a plain MLP
{
  const s = content("Model", 3, "12 · JC-PINN versus a plain MLP", "JC-PINN versus a plain MLP");
  const hdr = (t, al) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: STEEL }, align: al || "center", valign: "middle", fontSize: 13 } });
  const row = (m, t, g, note, hl) => {
    const f = { color: hl ? PALE : WHITE };
    return [
      { text: m, options: { bold: true, color: hl ? ORANGE : NAVY, fontSize: 14, valign: "middle", fill: f } },
      { text: t, options: { align: "center", valign: "middle", fontSize: 16, bold: true, color: NAVY, fill: f } },
      { text: g, options: { align: "center", valign: "middle", fontSize: 16, bold: true, color: NAVY, fill: f } },
      { text: note, options: { color: MUTED, fontSize: 13, valign: "middle", fill: f } },
    ];
  };
  s.addTable([
    [hdr("Model", "left"), hdr("Random 37-case test"), hdr("Unseen temp/rate groups (9-group mean)"), hdr("Note", "left")],
    row("Plain MLP, 5-16-16-1, 385 weights", "0.143", "11.90", "tried as an alternative; no JC backbone"),
    row("JC-PINN (selected)", "0.439", "6.23", "JC backbone × learned correction, λ = 0, 5 seeds", true),
    row("JC-PINN, JC equation switched off (control)", "0.338", "5.63", "post-hoc check, not used for selection; better on both"),
    row("JC equation alone", "7.37", "13.95", "too rigid: same curve shape for every condition"),
  ], { x: 0.6, y: 1.75, w: 12.1, colW: [3.6, 2.0, 2.6, 3.9], rowH: [0.6, 0.58, 0.58, 0.58, 0.58], border: { type: "solid", pt: 0.75, color: "D9E6F2" }, margin: [0.04, 0.12, 0.04, 0.12], fontFace: "Calibri", objectName: "why_table" });
  const callouts = [
    ["Familiar conditions", "On the random split the plain MLP is more accurate: 0.143 vs 0.439.", STEEL],
    ["Unseen temperature–rate groups", "JC-PINN 6.23 vs MLP 11.90, but these scores were used in selection: not an independent test of superiority.", ORANGE],
  ];
  callouts.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 6.15;
    card(s, x, 4.95, 5.95, 1.1, ICE);
    s.addShape(pres.shapes.OVAL, { x: x + 0.22, y: 5.12, w: 0.26, h: 0.26, fill: { color: col }, line: { color: col }, objectName: uid("flag") });
    text(s, h, { x: x + 0.62, y: 5.04, w: 5.2, h: 0.34, fontSize: 16, bold: true });
    text(s, b, { x: x + 0.62, y: 5.4, w: 5.2, h: 0.6, fontSize: 13.5, color: MUTED });
  });
  card(s, 0.6, 6.17, 12.1, 0.8, NAVY);
  text(s, [R("These comparisons do not show an accuracy benefit from the JC backbone or a physics penalty.  ", { color: ORANGE, bold: true }), R("Random-split scores measure interpolation between near-duplicate cases; the unseen-group test is closer to real prediction. Curve RMSE in MPa.", { color: WHITE })],
    { x: 0.85, y: 6.22, w: 11.6, h: 0.7, fontSize: 13.5, valign: "middle" });
  s.addNotes("All numbers are curve RMSE in megapascals; the user confirmed the units. The plain MLP, 5-16-16-1 with 385 weights, scores 0.143 on the random 37-case test and 11.90 on the nine hidden temperature-rate groups. The selected JC-PINN, physics-loss weight zero, five seeds, scores 0.439 and 6.23. The post-hoc control, the same network with the equation switched off, scores 0.338 and 5.63: better on both, and it was not used for selection. The JC equation alone scores 7.37 and 13.95. So the table does not show that the JC backbone or physics improves accuracy. The JC-PINN beats the plain MLP on hidden groups, but those group scores were part of model selection, so this is not an independent test of which model is better. Differences in architecture, output form and regularisation also prevent pinning the gap on a single ingredient.");
}

// ================================================================== 14 JC-PINN model + training GIF
{
  const s = content("Model", 3, "13 · Data modelling", "JC-PINN: a JC-backbone hybrid with a learned correction");
  card(s, 0.6, 1.7, 6.0, 2.62, NAVY);
  text(s, [R("σ = σ"), sub("JC"), R("(θ) · exp(δ)"), R("     λ = 0", { color: ORANGE, fontSize: 18 })], { x: 0.85, y: 1.8, w: 5.6, h: 0.55, fontSize: 26, bold: true, color: WHITE });
  text(s, [R("σ"), sub("JC"), R(" = [A − Bεⁿ][1 + C ln(ε̇/ε̇₀)][1 − T*ᵐ][G/G₀]"), sup("q"), R("[1 − φ]"), sup("r")], { x: 0.85, y: 2.38, w: 5.6, h: 0.36, fontSize: 14, color: WHITE });
  text(s, [
    R("ε = E11, total axial strain (not equivalent plastic strain)", { breakLine: true }),
    R("ε̇₀ = 10⁻⁵ /s  ·  T* = max[(T − 30)/(600 − 30), 0], T in °C", { breakLine: true }),
    R("G₀ = 25 300 MPa  ·  φ = 1 − ρ/2700 (confirmed by the user)", { breakLine: true }),
    R("A − Bεⁿ is a softening form, unlike standard JC A + Bεpⁿ"),
  ], { x: 0.85, y: 2.78, w: 5.6, h: 1.45, fontSize: 12.5, color: LINE, paraSpaceAfter: 2 });
  const facts = [
    ["δ network", "5 inputs → 16 → 16 → 1, tanh, starting at δ = 0 (the plain JC law)"],
    ["Parameters", "385 network weights and biases + 7 JC constants = 392 per member; 1 960 across 5 seeds"],
    ["Selected λ = 0", "No physics-residual penalty. Backbone and correction are not separately identifiable"],
    ["Training", "Adam 1 500 steps, then L-BFGS ≤ 2 500 iterations; weight decay α = 1; geometric mean of 5 seeds"],
  ];
  facts.forEach(([h, b], i) => {
    const y = 4.45 + i * 0.62;
    dot(s, 0.6, y + 0.04, String(i + 1), i === 2 ? ORANGE : STEEL, 0.34);
    text(s, [B(h + ": ", { color: NAVY }), R(b, { color: MUTED })], { x: 1.08, y, w: 5.55, h: 0.58, fontSize: 12.5 });
  });
  s.addImage({ path: A("gif_training.gif"), x: 6.85, y: 1.85, w: 5.9, h: 5.9 / 2.4, altText: "Animated: recorded JC-PINN training trace for four training cases, curves moving onto the simulation data as the loss falls", objectName: "gif_training" });
  card(s, 6.85, 4.5, 5.9, 1.4, ICE);
  text(s, [B("Watch it learn: "), R("at step 0 the model is the plain JC law (lines off the dots). Adam and then L-BFGS pull the four training curves towards the simulation data as the loss falls about 60-fold (0.171 → 0.0028).")],
    { x: 7.05, y: 4.6, w: 5.5, h: 1.2, fontSize: 13.5 });
  text(s, "Animated in Slide Show: recorded training trace, seed 0 (not a new run). Stress in MPa.", { x: 6.85, y: 6.0, w: 5.9, h: 0.3, fontSize: 11, color: MUTED });
  s.addNotes("The model multiplies the custom Johnson-Cook form by exp of delta, a small neural correction. In the equation, epsilon is E11, the total axial strain of the data, not the equivalent plastic strain of standard Johnson-Cook; the reference rate is ten to the minus five per second; T-star is temperature scaled between 30 and 600 degrees and clipped at zero; G-nought is 25,300 megapascals; and porosity enters only through density, using the user-confirmed mapping phi equals one minus rho over 2700. Note the A minus B epsilon to the n term: it is a softening form, unlike standard hardening Johnson-Cook. The selected physics-loss weight lambda is zero, so no physics residual penalty is active; the seven constants and the network are fitted jointly, and their separate contributions are not identifiable. Each member has 385 network weights and biases plus seven constants, 392 values; five members give 1,960. The animation is the recorded training trace for seed 0, not a new run.");
}

// ================================================================== 15 Evaluation: test GIF
pres.addSection({ title: "Evaluate" });
{
  const s = content("Evaluate", 4, "14 · Evaluation", "Scored on 37 simulations held out from fitting");
  s.addImage({ path: A("gif_test.gif"), x: 0.5, y: 1.7, w: 7.6, h: 7.6 / 2.4, altText: "Animated: JC-PINN prediction against each of the 37 held-out test curves, with the parity plot filling in to R² = 0.9995", objectName: "gif_test" });
  text(s, "Animated in Slide Show: each frame is one held-out case; the right panel collects every point.", { x: 0.6, y: 4.95, w: 7.4, h: 0.3, fontSize: 11, color: MUTED });
  const stats = [["0.4386", "mean of the 37 curve RMSEs (MPa)"], ["0.9995", "R² over 4 440 test points"], ["94.9 %", "of points within ±1 source stress unit"], ["37 / 37", "cases better than the JC law alone"]];
  stats.forEach(([v, l], i) => {
    const x = 8.5 + (i % 2) * 2.15, y = 1.8 + Math.floor(i / 2) * 1.55;
    card(s, x, y, 2.0, 1.38, i === 0 ? NAVY : ICE);
    text(s, v, { x: x + 0.15, y: y + 0.15, w: 1.8, h: 0.6, fontSize: 24, bold: true, color: i === 0 ? WHITE : (i === 3 ? ORANGE : NAVY) });
    text(s, l, { x: x + 0.15, y: y + 0.75, w: 1.75, h: 0.6, fontSize: 12, color: i === 0 ? LINE : MUTED });
  });
  card(s, 0.6, 5.35, 12.1, 1.5, ICE);
  text(s, [B("How to read it: "), R("37 simulations held out from fitting; scored after the model was locked. "), B("Not a blind test: ", { color: ORANGE }), R("the test cases were explored in earlier project stages. Worst curve 0.84 (case 10); pooled point RMSE 0.504. The JC law alone scores 7.37, so the correction cuts the error about 17-fold. The physics-disabled control scored 0.338 on the same cases.")],
    { x: 0.85, y: 5.45, w: 11.6, h: 1.3, fontSize: 14, valign: "middle" });
  s.addNotes("These 37 simulations were held out from fitting and scored after the model was locked. It is not a blind test: the same cases were explored in earlier project stages. The animation steps through every held-out case: the orange line is the prediction, the dots are the simulation. The mean of the 37 per-curve RMSEs is 0.4386 in megapascals; the pooled point RMSE is 0.504; the worst curve is 0.84, case 10. R squared is 0.9995 over 4,440 points, and 94.9 percent of points are within one source stress unit. Every one of the 37 cases beats the JC law alone, which averages 7.37. For balance: the physics-disabled control scored 0.338 on the same cases.");
}

// ================================================================== 16 Evaluation: by condition and limits
{
  const s = content("Evaluate", 4, "15 · Evaluation", "Where the model is strongest, and where to be careful");
  s.addChart(pres.charts.BAR, [{ name: "Test RMSE (MPa)", labels: ["30 °C · 10⁻⁵", "30 °C · 10⁻⁴", "30 °C · 10⁻³", "100 °C · 10⁻⁵", "100 °C · 10⁻⁴", "100 °C · 10⁻³", "200 °C · 10⁻⁴", "200 °C · 10⁻³"], values: [0.354, 0.803, 0.182, 0.434, 0.283, 0.454, 0.569, 0.143] }], Object.assign({}, AX, {
    x: 0.6, y: 1.7, w: 6.9, h: 4.4, barDir: "bar", barGapWidthPct: 45, chartColors: [HEX.dk2], showLegend: false,
    showTitle: true, title: "Held-out test error by temperature and strain rate (mean curve RMSE, MPa)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelFontSize: 12,
    catAxisOrientation: "maxMin", catAxisLabelFontSize: 12, valAxisMinVal: 0, valAxisMaxVal: 1.0, valAxisMajorUnit: 0.25, objectName: "condition_chart",
  }));
  const pts = [
    ["Strong", "Every group's mean curve RMSE is below 1. Lowest: 200 °C · 10⁻³ (0.14) and 30 °C · 10⁻³ (0.18); 100 °C · 10⁻³ is 0.45.", GREEN],
    ["Weakest", "30 °C · 10⁻⁴ (0.80): 8 test cases but only 1 training case at that condition.", ORANGE],
    ["Gaps in the data", "One case at 200 °C · 10⁻⁵ and none at 300 °C: predictions there are extrapolation.", STEEL],
    ["Density / porosity", "Matched density steps move stress by only ≈ 0.2; backbone exponent r ≈ 0 (the correction also sees density). Porosity-labelled data are needed.", NAVY],
  ];
  pts.forEach(([h, b, col], i) => {
    const y = 1.7 + i * 1.12;
    s.addShape(pres.shapes.OVAL, { x: 7.95, y: y + 0.08, w: 0.26, h: 0.26, fill: { color: col }, line: { color: col }, objectName: uid("flag") });
    text(s, h, { x: 8.4, y, w: 4.3, h: 0.36, fontSize: 17, bold: true });
    text(s, b, { x: 8.4, y: y + 0.38, w: 4.3, h: 0.72, fontSize: 13, color: MUTED });
  });
  text(s, "A plain MLP scored lower on familiar conditions (0.143 vs 0.439 test) but higher on unseen temperature–rate groups (11.90 vs 6.23); those group scores were used in selection, so they are not independent estimates. Stress in MPa (units confirmed by the user; no generator documentation).",
    { x: 0.6, y: 6.25, w: 12.1, h: 0.7, fontSize: 12.5, color: MUTED });
  s.addNotes("Broken down by condition, every held-out group has a mean curve RMSE under one megapascal; individual points can be larger, up to 2.9. The two lowest-error groups are 200 degrees and 30 degrees at the fast rate, 0.14 and 0.18; note that 100 degrees at the fast rate is 0.45, so this is not a fast-rate rule. The weakest group, 30 degrees at the middle rate, has eight test cases but only one in training. There is one case at 200 degrees and the slowest rate and none at 300 degrees, so predictions there are extrapolation. Density barely changes the curves; the backbone's porosity exponent is about zero, although the correction network also receives density. A plain MLP was better on familiar conditions but worse on hidden groups, and those group scores were used in selection.");
}

// ================================================================== 17-19 The locked model as an Ansys material (post-hoc)
// Added 17 Nov 2026. Numbers come from report/numbers.json (scripts/write_latex_numbers.py); figures from figures/.
pres.addSection({ title: "Deploy" });
const N = Object.fromEntries(Object.entries(require(path.join(__dirname, "..", "..", "report", "numbers.json")))
  .map(([k, v]) => [k, String(v).replace(/\{,\}/g, ",")]));
const sgn = (v) => String(v).replace("-", "−");
const FIG = (f) => path.join(__dirname, "..", "..", "figures", f);
{
  const s = content("Deploy", 5, "16 · From model to Ansys material", "The locked JC-PINN, generated into an Ansys user material");
  const steps = [
    ["Generate", "Abaqus UMAT and ANSYS USERMAT written from the locked weights; not refitted. J2 plasticity, radial return, consistent tangent.", NAVY],
    ["Verify offline", `Flow stress to ${N.VerStressErr} (relative), slope ${N.VerSlopeErr}, tangent ${N.VerTangentErr}; ${N.VerFlagChecks}/${N.VerFlagChecks} range flags correct.`, STEEL],
    ["Run in MAPDL 2024 R1", `One element to ε₁₁ = 0.12: matches the offline result to ${N.SeMaxDiff} MPa at all ${N.SePoints} substeps (tolerance ${N.SeTol}).`, ORANGE],
  ];
  steps.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.75, 3.85, 2.6, ICE);
    dot(s, x + 0.25, 1.95, String(i + 1), col, 0.44);
    text(s, h, { x: x + 0.85, y: 2.0, w: 2.9, h: 0.4, fontSize: 18, bold: true });
    text(s, b, { x: x + 0.25, y: 2.6, w: 3.4, h: 1.7, fontSize: 13.5, color: MUTED });
  });
  const stats = [[`${N.SeMaxDiff} MPa`, "MAPDL vs offline, single element"], [`${N.SeSFinal} MPa`, `final σ₁₁ (EQPS ${N.SeEqpsFinal}, flag ${N.SeFlagFinal})`], ["ν = 0.33", "assumed; elasticity from G"], ["offline only", "Abaqus UMAT not yet run in Abaqus"]];
  stats.forEach(([v, l], i) => {
    const x = 0.6 + i * 3.08;
    card(s, x, 4.6, 2.9, 1.35, i === 0 ? NAVY : ICE);
    text(s, v, { x: x + 0.2, y: 4.72, w: 2.6, h: 0.55, fontSize: 22, bold: true, color: i === 0 ? WHITE : (i === 3 ? ORANGE : NAVY) });
    text(s, l, { x: x + 0.2, y: 5.3, w: 2.6, h: 0.55, fontSize: 12, color: i === 0 ? LINE : MUTED });
  });
  text(s, "Strain E11 is read as plastic strain; outside the data the routines flag, they do not clamp. Evidence: umat/verification.json, umat/ansys_test/results_2026-11-17/.",
    { x: 0.6, y: 6.2, w: 12.1, h: 0.6, fontSize: 12.5, color: MUTED });
  s.addNotes(`After the model was locked, and without refitting it, we generated two user materials from its weights: an Abaqus UMAT and an ANSYS USERMAT. Both are J2 plasticity with a radial return and a consistent tangent; the flow stress is the JC-PINN prediction at the current plastic strain, and the elastic part comes from G and an assumed Poisson's ratio of 0.33. Offline they reproduce the Python model to a relative error of ${N.VerStressErr}, and the tangent to ${N.VerTangentErr}. We then built the USERMAT into MAPDL 2024 R1 and pulled one element to 12 percent strain: at all ${N.SePoints} substeps it matches the offline result to ${N.SeMaxDiff} megapascals, against a tolerance of ${N.SeTol}. The Abaqus version has only been checked offline.`);
}
{
  const s = content("Deploy", 5, "17 · Bracket", "The bracket with the JC-PINN, and what density alone does");
  s.addImage({ path: FIG("fig_bracket.png"), x: 0.6, y: 1.7, w: 6.0, h: 6.0 / 2.619, altText: "Bracket reaction for elastic, Workbench EP and JC-PINN USERMAT", objectName: "fig_bracket" });
  s.addImage({ path: FIG("fig_bracket_porosity.png"), x: 6.75, y: 1.7, w: 6.0, h: 6.0 / 2.6136, altText: "Bracket reaction for porosity cases", objectName: "fig_bracket_porosity" });
  card(s, 0.6, 4.2, 12.1, 2.65, ICE);
  text(s, [
    B("Same Workbench bracket, ", { color: NAVY }), R(`${N.MeshElemCoarse} SOLID186 elements, fixed support, imposed 2 mm; solved in MAPDL with three materials.`, { breakLine: true }),
    B("JC-PINN at φ = 4 %: ", { color: ORANGE }), R(`peak ${N.BrUsermatPeakkN} kN at −${N.BrUsermatPeakUX} mm, then softens to ${N.BrUsermatFinalkN} kN. The Workbench EP card is a different material condition (yield 251 MPa, hardening): a reference, not a validation.`, { breakLine: true }),
    B("Density only, G fixed: ", { color: NAVY }), R(`φ 0 → 7.85 % changes the peak by ${sgn(N.PorDensPeakChangePct)} % (single element ${sgn(N.PorSeDensYieldPct)} %).`, { breakLine: true }),
    B("G matters more: ", { color: ORANGE }), R(`about ${N.PorBrGOverDens}× per percent change. G(φ) is unknown, so this is only the density part of the porosity effect.`),
  ], { x: 0.85, y: 4.35, w: 11.6, h: 2.4, fontSize: 14.5, paraSpaceAfter: 6 });
  s.addNotes(`This is the project's Workbench bracket, unchanged: ${N.MeshElemCoarse} quadratic elements, a fixed support and an imposed displacement of 2 millimetres, solved in MAPDL with three materials. The JC-PINN at the 4 percent study point peaks at ${N.BrUsermatPeakkN} kilonewtons and then softens to ${N.BrUsermatFinalkN}. The Workbench elastic-plastic card is a different material condition, so it is a reference, not a validation. On the right, with G fixed, going from 0 to 7.85 percent porosity changes the peak by only ${N.PorDensPeakChangePct} percent, which matches the single-element ${N.PorSeDensYieldPct} percent. Per percent change, G acts about ${N.PorBrGOverDens} times more strongly, and G as a function of porosity is unknown, so this is only the density part of the porosity effect.`);
}
{
  const s = content("Deploy", 5, "18 · Mesh study", "The softening makes the bracket result mesh dependent");
  s.addImage({ path: FIG("fig_mesh_ep.png"), x: 0.6, y: 1.7, w: 7.6, h: 7.6 / 2.6136, altText: "Bracket reaction and peak plastic strain on two meshes, JC-PINN and Workbench EP", objectName: "fig_mesh_ep" });
  const stats = [[`${sgn(N.BrMeshPeakChangePct)} %`, "JC-PINN peak force, 5 → 2.5 mm"], [`${sgn(N.MeshForceOneChangePct)} %`, "JC-PINN force at 1 mm"], [`≤ ${N.MeshEpMaxChangePct} %`, "hardening EP card, same meshes"], [`${N.MeshEqpsCoarse} → ${N.MeshEqpsFine}`, "JC-PINN peak plastic strain"]];
  stats.forEach(([v, l], i) => {
    const x = 8.5 + (i % 2) * 2.15, y = 1.75 + Math.floor(i / 2) * 1.55;
    card(s, x, y, 2.0, 1.38, i === 0 ? NAVY : ICE);
    text(s, v, { x: x + 0.15, y: y + 0.15, w: 1.8, h: 0.6, fontSize: 22, bold: true, color: i === 0 ? WHITE : (i === 2 ? GREEN : NAVY) });
    text(s, l, { x: x + 0.15, y: y + 0.75, w: 1.75, h: 0.6, fontSize: 12, color: i === 0 ? LINE : MUTED });
  });
  card(s, 0.6, 4.95, 12.1, 1.9, ICE);
  text(s, [
    B(`Uniform 2×2×2 split (${N.MeshElemCoarse} → ${N.MeshElemFine} elements), not a Workbench remesh. `), R("Same geometry, supports and load.", { breakLine: true }),
    B("Bracket forces after yield are mesh-specific, not a converged strength. ", { color: ORANGE }), R("The softening causes it; a regularised softening law is future work.", { breakLine: true }),
    R("One material condition · small strain · ν = 0.33 assumed · nothing validated experimentally.", { color: MUTED }),
  ], { x: 0.85, y: 5.05, w: 11.6, h: 1.7, fontSize: 14.5, paraSpaceAfter: 5, valign: "middle" });
  s.addNotes(`To test the mesh, we split every element two by two by two: ${N.MeshElemFine} elements with the same geometry, supports and load. This is a uniform split, not a Workbench remesh. With the JC-PINN the peak force changes by ${N.BrMeshPeakChangePct} percent, and the force at one millimetre by ${N.MeshForceOneChangePct} percent. The peak plastic strain rises from ${N.MeshEqpsCoarse} to ${N.MeshEqpsFine} and keeps rising. The same split with the hardening Workbench card changes the force by at most ${N.MeshEpMaxChangePct} percent, so the softening causes the dependence. The bracket forces after yield are therefore specific to the mesh, not a converged strength. A regularised softening law is future work.`);
}

// ================================================================== 20 Deployment (planned)
{
  const s = content("Deploy", 5, "19 · Deployment · partly built, mostly planned", "Planned: a bracket-check concept for aerospace companies");
  const flow = [
    ["Company inputs", "CT-scan porosity and largest pore (needs a pore-to-crack convention) · temperature · load rate", NAVY, "PLANNED"],
    ["JC-PINN inference", "Predicts Svm(E11) for given conditions, with range warnings", CYAN, "EXISTS"],
    ["Material card", "Writer exists (CSV / APDL / XML), untested template; E11 → εp needs a confirmed E", STEEL, "EXISTS"],
    ["Bracket analysis", "USERMAT runs the bracket in MAPDL (verified, not validated; mesh dependent after yield)", STEEL, "EXISTS"],
    ["Fracture check", [R("Specify crack geometry and orientation; K"), sub("I"), R("(a) from the crack-opening stress; solve K"), sub("I"), R("(a"), sub("c"), R(") = K"), sub("IC"), R("; check LEFM or use J")], ORANGE, "PLANNED"],
  ];
  flow.forEach(([h, b, col, tag], i) => {
    const x = 0.6 + i * 2.48, w = 2.25;
    card(s, x, 1.75, w, 2.55, i === 4 ? NAVY : ICE);
    dot(s, x + 0.2, 1.92, String(i + 1), col, 0.4);
    const ok = tag === "EXISTS";
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + w - 1.0, y: 1.98, w: 0.82, h: 0.28, rectRadius: 0.06, fill: { color: ok ? GREEN : "3A4A6B" }, line: { color: ok ? GREEN : "3A4A6B" }, objectName: uid("chip") });
    text(s, tag, { x: x + w - 1.0, y: 1.98, w: 0.82, h: 0.28, fontSize: 10, bold: true, color: WHITE, align: "center", valign: "middle" });
    text(s, h, { x: x + 0.2, y: 2.42, w: w - 0.35, h: 0.4, fontSize: 15, bold: true, color: i === 4 ? ORANGE : NAVY });
    text(s, b, { x: x + 0.2, y: 2.85, w: w - 0.3, h: 1.4, fontSize: 12, color: i === 4 ? WHITE : MUTED });
    if (i < flow.length - 1) text(s, "›", { x: x + w, y: 2.7, w: 0.23, h: 0.6, fontSize: 30, color: LINE, align: "center" });
  });
  const dec = [["Accept", [R("largest crack-equivalent pore well below a"), sub("c")], GREEN], ["Inspect", [R("close to a"), sub("c"), R(": re-scan or test")], ORANGE], ["Reject", [R("at or above a"), sub("c")], "C0392B"]];
  text(s, "DECISION CONCEPT · PENDING FATIGUE ANALYSIS, MARGINS AND VALIDATION", { x: 0.6, y: 4.5, w: 7.3, h: 0.26, fontSize: 11, bold: true, color: STEEL, charSpacing: 2 });
  dec.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 2.48;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.88, w: 2.25, h: 1.0, rectRadius: 0.1, fill: { color: col }, line: { color: col }, objectName: uid("decision") });
    text(s, h, { x: x + 0.2, y: 4.95, w: 1.9, h: 0.36, fontSize: 16, bold: true, color: WHITE });
    text(s, b, { x: x + 0.2, y: 5.32, w: 1.95, h: 0.52, fontSize: 12, color: WHITE });
  });
  text(s, "A static critical crack size alone is not a fatigue-life or airworthiness criterion; cyclic flight loading needs a fatigue / damage-tolerance assessment.", { x: 0.6, y: 6.0, w: 7.3, h: 0.6, fontSize: 12.5, color: MUTED });
  card(s, 8.05, 4.5, 4.65, 2.4, ICE);
  text(s, "STATUS ON MAIN", { x: 8.3, y: 4.63, w: 4.2, h: 0.26, fontSize: 11, bold: true, color: STEEL, charSpacing: 3 });
  text(s, [
    B("Exists: ", { color: GREEN }), R("locked JC-PINN inference with range warnings; porosity material-study workflow; material-card writer; ANSYS USERMAT and Abaqus UMAT (verified, not validated).", { breakLine: true }),
    B("Planned: ", { color: ORANGE }), R("regularised softening, crack model and K"), sub("IC"), R(", fatigue assessment and the decision tool. The older Model Studio app is archived."),
  ], { x: 8.3, y: 4.95, w: 4.25, h: 1.9, fontSize: 12.5, paraSpaceAfter: 6 });
  s.addNotes("This slide separates what exists from what is planned. On the main branch today: the locked JC-PINN can be run for given conditions with range warnings; a porosity material-study workflow uses it; and a material-card writer can export CSV, APDL or XML tables, though it is an unvalidated template, and converting total axial strain to plastic strain needs a confirmed Young's modulus. The JC-PINN now runs in the Ansys bracket model as a user material: it is verified, not validated, and its results after yield depend on the mesh. Still planned: a regularised softening law; a fracture check with a specified crack geometry and orientation, a stress intensity from the crack-opening stress, and a toughness source; and the decision tool. Accept, inspect or reject is a concept only: a static critical crack size is not a fatigue or airworthiness criterion. The older Model Studio app has been archived.");
}

// ================================================================== 18 Limits and open questions
pres.addSection({ title: "Limits" });
{
  const s = content("Limits", 4, "20 · Limits and open questions", "What we have not shown");
  const blocks = [
    ["Evidence", "The test set is not blind. Case 60 (200 °C, 10⁻⁵ /s) is a single irregular case. The team's Ansys comparison set-up is not archived. No experimental validation. Bracket results after yield depend on the mesh (softening): not a converged strength.", ORANGE],
    ["Definitions", "Units (MPa etc.) and density-as-porosity confirmed by the user, but no generator documentation: Svm's spatial averaging and generating solver are unknown; Evm is not established as accumulated plastic strain; why every curve ends below its start is unexplained.", STEEL],
    ["Porosity", "Represented through density, φ = 1 − ρ/2700 (confirmed by the user; cases at 0, 3 and 7.85 %; 4 % study point = 2592 kg/m³). Backbone exponent r ≈ 0, but the correction also sees density; this does not show real pores are harmless.", NAVY],
    ["CL not yet computed", [R("Needs crack geometry and orientation, a pore-to-crack convention, a K"), sub("IC"), R(" source, K"), sub("I"), R("(a) from the crack-opening stress, an LEFM check (or J), and fatigue assessment for cyclic loads. To confirm with the professor.")], CYAN],
  ];
  blocks.forEach(([h, b, col], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.75 + Math.floor(i / 2) * 2.6;
    card(s, x, y, 5.95, 2.42, ICE);
    dot(s, x + 0.25, y + 0.25, String(i + 1), col, 0.48);
    text(s, h, { x: x + 0.9, y: y + 0.28, w: 4.85, h: 0.4, fontSize: 19, bold: true });
    text(s, b, { x: x + 0.9, y: y + 0.78, w: 4.85, h: 1.6, fontSize: 14, color: MUTED });
  });
  s.addNotes("Before concluding, what we have not shown. Evidence: the test set is not blind, case 60 is a single irregular case the model cannot fully reproduce, the team's Ansys comparison set-up was not archived, and nothing is validated against experiments. On the bracket, the softening makes results after yield depend on the mesh, so the bracket forces are not a converged strength. Definitions: the user confirmed the units and that density stands for porosity, but we have not seen the generator's documentation, so Svm's spatial averaging and the solver that generated it are unknown; Evm is not established as accumulated plastic strain; and we do not know why every curve ends below its start. Porosity: it enters through density, using the user-confirmed mapping phi equals one minus rho over 2700, which gives 0, 3 and 7.85 percent for the cases and 2592 for our 4 percent study point. The backbone's porosity exponent is about zero, but the correction also sees density, and this says nothing about whether real pores are harmless. Finally, the critical flaw size is not computed: it needs a crack model, a toughness source, a stress intensity from the crack-opening stress, a validity check, and a fatigue assessment.");
}

// ================================================================== 19 Conclusion
pres.addSection({ title: "Close" });
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Close" });
  s.addText("CONCLUSION", { placeholder: "kicker" });
  s.addText("What we showed, and what comes next", { placeholder: "title" });
  const pts = [
    ["Bracket set-up and Ansys peaks", "With an upper-half bore load, the team's plastic runs peak at the bore. The elastic peak is 1.86× the built-in JC peak (set-up details not archived)."],
    ["A single-peak agreement only", "JC-U's peak is within 0.94 % of built-in JC. This does not validate the material law, the full response or JC-PINN-to-Ansys coupling."],
    ["An accurate JC-backbone hybrid", "0.4386 mean curve RMSE on 37 held-out cases (R² 0.9995; 37/37 better than the JC law alone). λ = 0, and the physics-disabled control did better: no accuracy benefit from physics is shown."],
    ["Next: critical flaw size · PLANNED", [R("Define crack geometry, orientation and K"), sub("IC"), R("; compute K"), sub("I"), R("(a) from the crack-opening stress; regularise the softening (mesh dependence), measure G(φ) and add fatigue before any decision tool.")]],
  ];
  pts.forEach(([h, b], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.75 + Math.floor(i / 2) * 2.42;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.95, h: 2.25, rectRadius: 0.1, fill: { color: "13305A" }, line: { color: i === 3 ? HEX.accent1 : "13305A", width: 1.5 }, objectName: uid("concl") });
    text(s, String(i + 1).padStart(2, "0"), { x: x + 0.3, y: y + 0.15, w: 1.0, h: 0.5, fontSize: 24, bold: true, color: i === 3 ? ORANGE : CYAN });
    text(s, h, { x: x + 0.3, y: y + 0.65, w: 5.4, h: 0.4, fontSize: 18, bold: true, color: i === 3 ? ORANGE : WHITE });
    text(s, b, { x: x + 0.3, y: y + 1.08, w: 5.4, h: 1.1, fontSize: 13.5, color: PALE });
  });
  text(s, "Ansys results: team screenshots, not independently re-run. Material-data units confirmed by the user (no generator documentation). No experimental validation.", { x: 0.6, y: 6.68, w: 11, h: 0.3, fontSize: 11, color: LINE });
  s.addNotes("To conclude. With the upper-half bore load, the team's plastic Ansys runs peak at the bore, and the elastic peak is 1.86 times the built-in Johnson-Cook peak; the set-up details were not archived. The user-defined run's peak is within 0.94 percent of the built-in one, but that single number does not validate the material law, the full response or any coupling from our model. Our JC-backbone hybrid reproduces the 37 held-out simulations to a mean curve RMSE of 0.4386, R squared 0.9995, and beats the JC law alone on every case. Its selected physics-loss weight is zero and the physics-disabled control did better, so we do not claim an accuracy benefit from physics. Next, still planned: a crack model with toughness, the stress intensity from the crack-opening stress, a validated Ansys coupling and a fatigue assessment, before any decision tool.");
}

// ================================================================== 20 Thank you
{
  const s = pres.addSlide({ masterName: "COVER", sectionTitle: "Close" });
  s.addText("Thank you", { placeholder: "title" });
  text(s, "Any Questions?", { x: 0.7, y: 3.8, w: 7.5, h: 0.9, fontSize: 36, bold: true, color: ORANGE });
  text(s, "Pranav Parasuram C  ·  R Saravanan  ·  Dinesh Y  ·  Amit Narayan K", { x: 0.7, y: 5.4, w: 8.5, h: 0.35, fontSize: 16, color: WHITE });
  text(s, "Multiscale Modelling of Materials using Machine Learning  ·  IIITDM Kancheepuram", { x: 0.7, y: 5.85, w: 8.5, h: 0.32, fontSize: 14, color: LINE });
  s.addNotes("Thank you. We are happy to take any questions.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
