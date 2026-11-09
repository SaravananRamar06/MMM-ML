// Builds "Final Presentation - Porosity in an AM Wing Bracket.pptx" (20 slides).
// Run: NODE_PATH=<dir containing pptxgenjs> node build_final.js <dir containing scripts/apply_theme.js>
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(path.join(process.argv[2], "scripts/apply_theme.js"));

const A = (f) => path.join(__dirname, "..", "assets", f);
const OUT = path.join(__dirname, "..", "Final Presentation - Porosity in an AM Wing Bracket.pptx");

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
  text(s, "From AlSi10Mg material data to bracket stress, with a physics-informed neural network and Ansys", { x: 0.7, y: 3.8, w: 7.4, h: 0.7, fontSize: 17, italic: true, color: LINE });
  const team = [["Pranav Parasuram C", "ME24B1061"], ["R Saravanan", "ME24I1006"], ["Dinesh Y", "ME24B1043"], ["Amit Narayan K", "ME24I1024"]];
  text(s, "TEAM", { x: 0.7, y: 4.75, w: 2, h: 0.25, fontSize: 11, bold: true, color: CYAN, charSpacing: 3 });
  team.forEach(([nm, roll], i) => {
    const x = 0.7 + (i % 2) * 3.4, y = 5.05 + Math.floor(i / 2) * 0.42;
    text(s, [B(nm, { color: WHITE }), R("   " + roll, { color: LINE, fontSize: 13 })], { x, y, w: 3.3, h: 0.36, fontSize: 16 });
  });
  text(s, [B("Course instructor  ", { color: CYAN }), R("Prof. Arul Kumar Mariyappan", { color: WHITE })], { x: 0.7, y: 6.05, w: 7.5, h: 0.32, fontSize: 15 });
  text(s, "Indian Institute of Information Technology, Design and Manufacturing (IIITDM) Kancheepuram", { x: 0.7, y: 6.45, w: 8.5, h: 0.32, fontSize: 14, color: LINE });
  s.addNotes("Good morning. We are presenting our course project on how porosity from 3D printing affects an aluminium aircraft wing bracket, and how a physics-informed neural network and Ansys work together to assess it.");
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
  const s = content("Problem", 0, "02 · Objective", "Predict the safe flaw size as porosity rises");
  const obj = [
    ["Learn the material", "Train a neural network on the 73 AlSi10Mg simulations we were given, to predict the stress–strain curve for any temperature, strain rate, density and shear modulus."],
    ["Load the bracket", "Feed those curves into Ansys and find the stress at the bracket's critical location under its real service load."],
    ["Predict the critical flaw length", "Combine that stress with fracture mechanics to get CL against porosity, the number a designer can act on."],
  ];
  obj.forEach(([h, b], i) => {
    const y = 1.8 + i * 1.3;
    card(s, 0.6, y, 6.7, 1.15, ICE);
    dot(s, 0.85, y + 0.33, String(i + 1), i === 2 ? ORANGE : STEEL, 0.48);
    text(s, h, { x: 1.55, y: y + 0.14, w: 5.6, h: 0.35, fontSize: 18, bold: true });
    text(s, b, { x: 1.55, y: y + 0.5, w: 5.6, h: 0.62, fontSize: 14, color: MUTED });
  });
  card(s, 7.7, 1.8, 5.0, 3.75, NAVY);
  text(s, "TARGET QUANTITY", { x: 8.0, y: 2.05, w: 4.4, h: 0.26, fontSize: 11, bold: true, color: CYAN, charSpacing: 3 });
  text(s, [R("C"), sub("L"), R(" = (1/π) · (K"), sub("IC"), R(" ⁄ Y σ)²")], { x: 8.0, y: 2.5, w: 4.5, h: 0.8, fontSize: 32, bold: true, color: WHITE });
  const terms = [["σ", "stress at the critical location (Ansys)", 3.5], ["K", [R("K"), sub("IC"), R(": source and porosity dependence still to be defined (no toughness data supplied)")], 4.0], ["Y", "shape factor of the flaw", 4.8]];
  terms.forEach(([sy, d, y]) => {
    text(s, sy, { x: 8.0, y, w: 0.4, h: 0.4, fontSize: 18, bold: true, color: ORANGE });
    text(s, d, { x: 8.45, y: y + 0.03, w: 4.05, h: 0.7, fontSize: 14, color: WHITE });
  });
  text(s, [R("CL is the "), B("critical flaw length"), R(": the largest pore or crack the bracket can carry at its working stress before it fractures. Study point: porosity φ = 4 % (assumed).")],
    { x: 0.6, y: 5.85, w: 12.1, h: 0.75, fontSize: 16 });
  s.addNotes("We have three objectives. First, learn the material behaviour from the professor's 73 simulations using a neural network. Second, put that behaviour into Ansys and find the stress in the bracket. Third, combine the stress with fracture mechanics to get the critical flaw length, CL, as porosity changes. CL is the biggest flaw the bracket can carry before it breaks.");
}

// ================================================================== 4 Roadmap / life cycle
{
  const s = content("Problem", null, "03 · Our approach", "The data science life cycle we followed");
  const st = [
    ["Problem", "Porosity in a printed wing bracket; target CL(φ)", NAVY],
    ["CAD & Ansys", "Bracket geometry, loads, supports; 3 material models", STEEL],
    ["EDA", "73 simulations explored: coverage, trends, key inputs", STEEL],
    ["Model", "Physics-informed NN (JC-PINN) chosen and trained", CYAN],
    ["Evaluate", "Scored after locking on 37 held-out simulations", CYAN],
    ["Deploy", "A bracket-check tool for aerospace companies", ORANGE],
  ];
  s.addShape(pres.shapes.LINE, { x: 1.2, y: 2.62, w: 10.9, h: 0, line: { color: PALE, width: 3 }, objectName: "life_line" });
  st.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 2.05;
    s.addShape(pres.shapes.OVAL, { x: x + 0.38, y: 2.2, w: 0.84, h: 0.84, fill: { color: col }, line: { color: WHITE, width: 3 }, objectName: uid("stage") });
    text(s, String(i + 1).padStart(2, "0"), { x: x + 0.38, y: 2.2, w: 0.84, h: 0.84, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle" });
    text(s, h, { x, y: 3.25, w: 1.9, h: 0.38, fontSize: 17, bold: true, align: "center", color: col });
    text(s, b, { x: x + 0.05, y: 3.68, w: 1.8, h: 1.1, fontSize: 13, color: MUTED, align: "center" });
  });
  card(s, 0.6, 5.15, 12.1, 1.55, ICE);
  text(s, "WHY IT IS MULTISCALE", { x: 0.9, y: 5.32, w: 4, h: 0.26, fontSize: 11, bold: true, color: STEEL, charSpacing: 3 });
  text(s, [B("Material scale: "), R("the neural network learns how AlSi10Mg flows under temperature and strain rate.   "), B("Part scale: "), R("Ansys uses that behaviour to load the full bracket.   "), B("Decision: "), R("fracture mechanics turns the bracket stress into a safe flaw size.")],
    { x: 0.9, y: 5.65, w: 11.5, h: 0.95, fontSize: 15 });
  s.addNotes("This is the path through the talk, following the data science life cycle: define the problem, model the bracket in Ansys, explore the data, build and evaluate the model, and finally deploy it. It is multiscale because the network works at the material scale, Ansys at the part scale, and fracture mechanics turns the result into a decision.");
}

// ================================================================== 5 CAD + loads + supports
pres.addSection({ title: "CAD and Ansys" });
{
  const s = content("CAD and Ansys", 1, "04 · CAD model, loads and supports", "Rib Bracket.STEP: geometry, loads and supports");
  img(s, "forces.png", 0.5, 1.7, 6.3, 1.5495, "Bracket planform with the bearing force F on the upper half of the bore, fixed supports on both mounting faces, reactions R and moment M = F × 210 mm");
  const rows = [
    ["Envelope", "231.5 × 230 × 40 mm plate"],
    ["Volume · mass", "778 cm³ · ≈ 2.1 kg (fully dense)"],
    ["Material", "AlSi10Mg, laser powder-bed fusion"],
    ["Load F", "Bearing load along +Y on the upper half of the Ø10 mm bore (628 mm² face)"],
    ["Supports", "Fixed in all directions on both 50 × 40 mm spar mounting faces"],
    ["Reactions", "R = F and M = F × 210 mm at the spar"],
    ["Load path", "Lower arm in tension, diagonal arm in compression"],
  ];
  s.addTable(rows.map(([k, v], i) => [
    { text: k, options: { bold: true, color: i === 3 ? ORANGE : NAVY, fontSize: 13, valign: "middle", fill: { color: i % 2 ? WHITE : ICE } } },
    { text: v, options: { color: NAVY, fontSize: 13, valign: "middle", fill: { color: i % 2 ? WHITE : ICE } } },
  ]), { x: 7.55, y: 1.7, w: 5.2, colW: [1.45, 3.75], rowH: 0.41, border: { type: "none" }, margin: [0.03, 0.1, 0.03, 0.1], fontFace: "Calibri", objectName: "cad_table" });
  img(s, "bore_compact.png", 7.85, 4.95, 4.6, 2.335, "Two bore close-ups: a load on the whole bore pulls the lower half into the hole; a pin load presses only on the upper half");
  card(s, 0.6, 5.95, 6.6, 0.9, ICE);
  text(s, [B("Why only the upper half? ", { color: ORANGE }), R("A pin can only push: it bears on the half of the bore the load drives it into, and the lower half opens a gap. Loading the whole bore would pull on the lower half and halve the bearing stress.")],
    { x: 0.8, y: 6.02, w: 6.25, h: 0.78, fontSize: 13, valign: "middle" });
  s.addNotes("This one slide carries the whole structural set-up. The bracket is a 40 mm thick AlSi10Mg plate with two arms meeting at a 10 mm bore. The pin load F acts upward on the upper half of the bore. Both mounting faces bolt to the spar and are fixed. Statics gives a reaction equal to F and a moment of F times the 210 mm lever arm, with the lower arm in tension and the diagonal arm in compression. We load only the upper half of the bore because a pin can only push; the lower half separates.");
}

// ================================================================== 6 Ansys set-up
{
  const s = content("CAD and Ansys", 1, "05 · Ansys simulations", "Three explicit simulations: only the material model changes");
  text(s, [R("Workbench project "), B("Comparison Study - Final"), R(": three "), B("Explicit Dynamics (AUTODYN)"), R(" systems on the same bracket and the same bore load. Any difference in the results comes from the material law.")],
    { x: 0.6, y: 1.7, w: 12.1, h: 0.6, fontSize: 16 });
  const sims = [
    ["A · Elastic", "EL", "curve_el.png", "σ = E·ε", "Linear and never yields. Card: density, E, ν.", STEEL],
    ["B · Elasto-plastic JC", "JC-B", "curve_jcb.png", "σy = (A + B εpⁿ)(1 + C ln ε̇*)(1 − T*ᵐ)", "Ansys' built-in Johnson–Cook strength: yield, hardening, strain-rate and temperature terms.", NAVY],
    ["C · User-defined JC", "JC-U", "curve_jcu.png", "our (εp, σ) table", "Multilinear hardening table from our customised JC law (table source to be confirmed). The formula has G and porosity terms, but the fitted porosity exponent r ≈ 0: density moves stress by only ≈ 0.2 (inferred MPa) in the data.", ORANGE],
  ];
  sims.forEach(([h, code, file, f, b, col], k) => {
    const x = 0.6 + k * 4.12, w = 3.85;
    card(s, x, 2.5, w, 4.3, ICE);
    text(s, [B(code + "  ", { color: col }), R(h, { color: NAVY, bold: true })], { x: x + 0.2, y: 2.62, w: w - 0.4, h: 0.38, fontSize: 16 });
    img(s, file, x + 0.45, 3.05, w - 0.9, 1.3206, `${h} schematic stress-strain curve`);
    text(s, f, { x: x + 0.2, y: 5.2, w: w - 0.4, h: 0.35, fontSize: 13.5, bold: true, color: col === NAVY ? STEEL : col });
    text(s, b, { x: x + 0.2, y: 5.55, w: w - 0.4, h: 1.2, fontSize: 12.5, color: NAVY });
  });
  s.addNotes("We ran three explicit dynamics simulations in Ansys. They share the geometry, mesh set-up and bore load, and differ only in the material card. A is purely elastic. B is elasto-plastic, using Ansys' built-in Johnson-Cook strength model. C is our user-defined Johnson-Cook, where we type in the hardening curve point by point from our own customised Johnson-Cook law, which also carries shear modulus and porosity terms; in our fit the porosity exponent comes out at about zero, because density barely changes the stress in the data.");
}

// ================================================================== 7 Ansys results
{
  const s = content("CAD and Ansys", 1, "06 · Ansys results", "Equivalent stress at t = 0.06 s");
  const sims = [
    ["EL", "Elastic", STEEL, "result_el.png", 1.3701, "595.27", "at the fixed corner of the upper mounting face"],
    ["JC-B", "Elasto-plastic JC", NAVY, "result_jcb.png", 1.3701, "320.79", "around the bore, where the load enters"],
    ["JC-U", "User-defined JC", ORANGE, "result_jcu.png", 1.3876, "323.81", "around the bore, where the load enters"],
  ];
  sims.forEach(([c, nme, col, file, ratio, mx, where], k) => {
    const x = 0.6 + k * 4.12, w = 3.85;
    card(s, x, 1.7, w, 4.95, ICE);
    text(s, [B(c + "  ", { color: col }), R(nme, { color: MUTED })], { x: x + 0.2, y: 1.82, w: w - 0.4, h: 0.38, fontSize: 17 });
    img(s, file, x + 0.15, 2.3, w - 0.3, ratio, `${nme}: von Mises stress contour at 0.06 s, maximum ${mx} MPa`);
    text(s, "peak von Mises stress", { x: x + 0.2, y: 5.05, w: w - 0.4, h: 0.28, fontSize: 12.5, color: MUTED });
    text(s, [B(mx, { color: col === NAVY ? STEEL : col }), R(" MPa", { color: NAVY, fontSize: 17 })], { x: x + 0.2, y: 5.33, w: w - 0.4, h: 0.6, fontSize: 32 });
    text(s, where, { x: x + 0.2, y: 5.98, w: w - 0.4, h: 0.6, fontSize: 14 });
  });
  text(s, "Ansys results supplied by the team; not independently re-run.", { x: 0.6, y: 6.72, w: 12.1, h: 0.28, fontSize: 11, color: MUTED });
  s.addNotes("These are the von Mises stress contours, all at 0.06 seconds. The colour scales differ between pictures, so read the legend numbers. The elastic run peaks at 595 megapascals at the fixed corner of the upper mounting face. Both Johnson-Cook runs peak at about 321 to 324 megapascals around the bore.");
}

// ================================================================== 8 Ansys comparison
{
  const s = content("CAD and Ansys", 1, "07 · Ansys comparison", "Plasticity halves the peak, and our curve matches Ansys");
  s.addChart(pres.charts.BAR, [{ name: "Peak von Mises stress (MPa)", labels: ["EL", "JC-B", "JC-U"], values: [595.27, 320.79, 323.81] }], Object.assign({}, AX, {
    x: 0.6, y: 1.7, w: 5.6, h: 4.45, barDir: "col", barGapWidthPct: 70, chartColors: [HEX.dk2, HEX.dk1, HEX.accent1], showLegend: false,
    showTitle: true, title: "Peak von Mises stress at t = 0.06 s (MPa)", showValue: true, dataLabelPosition: "outEnd", dataLabelFontBold: true, dataLabelFormatCode: "0.0",
    catAxisLabelFontBold: true, valAxisMinVal: 0, valAxisMaxVal: 700, valAxisMajorUnit: 100, objectName: "peak_chart",
  }));
  const finds = [
    ["1.85×", "Elastic overpredicts", "It cannot yield, so its stress keeps rising: 595 MPa against about 322 MPa for both JC runs.", STEEL],
    ["0.94 %", "JC-U agrees with JC-B", "323.81 vs 320.79 MPa: our user-defined curve behaves like Ansys' own Johnson–Cook model.", ORANGE],
    ["Bore", "The peak moves to the bore", "With plasticity, the hot spot sits where the pin load enters: the location σ is read from for CL.", NAVY],
  ];
  finds.forEach(([big, h, b, col], i) => {
    const y = 1.7 + i * 1.55;
    card(s, 6.6, y, 6.1, 1.38, ICE);
    text(s, big, { x: 6.8, y: y + 0.2, w: 1.7, h: 0.95, fontSize: 30, bold: true, color: col === NAVY ? STEEL : col, valign: "middle" });
    text(s, h, { x: 8.55, y: y + 0.15, w: 4.0, h: 0.36, fontSize: 17, bold: true });
    text(s, b, { x: 8.55, y: y + 0.53, w: 4.0, h: 0.8, fontSize: 13.5, color: MUTED });
  });
  text(s, "JC-U is the route for our own material curves to drive the bracket model.", { x: 0.6, y: 6.28, w: 12.1, h: 0.35, fontSize: 16, bold: true, color: ORANGE });
  text(s, "Ansys results supplied by the team; not independently re-run.", { x: 0.6, y: 6.7, w: 12.1, h: 0.28, fontSize: 11, color: MUTED });
  s.addNotes("Three findings. The elastic model gives a peak 1.85 times higher, because it never yields. The two Johnson-Cook runs agree within one percent, so our user-defined curve behaves like Ansys' own model. And with plasticity the peak moves to the bore, which is where we read the stress for the critical flaw length. That is why JC-U is the route for our own material curves.");
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
    ["Density ρ", "2488 · 2619 · 2700 kg/m³; porosity inferred from density: 0 / 3 / 7.85 % (2700 / 2619 / 2488), pending confirmation by the professor"],
    ["Shear modulus G", "23 314 · 24 541 · 25 300 MPa (inferred)"],
    ["Output", "von Mises stress Svm along axial strain E11 = 0–10 %"],
  ];
  const ys = [2.3, 2.92, 3.54, 4.72, 5.36];
  vars.forEach(([k, v], i) => {
    const y = ys[i];
    text(s, k, { x: 7.6, y, w: 4.9, h: 0.3, fontSize: 15, bold: true, color: i === 4 ? ORANGE : NAVY });
    text(s, v, { x: 7.6, y: y + 0.31, w: 4.9, h: i === 2 ? 0.68 : 0.34, fontSize: 13.5, color: MUTED });
  });
  text(s, "Units (°C, /s, kg/m³, MPa) inferred from the data, unconfirmed; stress units inferred as MPa (unconfirmed).", { x: 7.6, y: 6.2, w: 4.9, h: 0.48, fontSize: 11.5, color: STEEL, bold: true });
  s.addNotes("The professor gave us a design matrix of 108 simulations; 73 have results, about 2.2 million rows of history. Every cell of temperature and strain rate has 9 combinations of density and shear modulus, except 200 degrees at the slowest rate, which has only one case, and 300 degrees, which has none. The porosity values next to density are our inference, assuming fully dense is 2700.");
}

// ================================================================== 10 EDA: curves and factor effects
{
  const s = content("EDA", 2, "09 · Exploratory data analysis", "Temperature and strain rate drive the curves");
  img(s, "eda_curves.png", 0.45, 1.65, 7.9, 2.5581, "All 73 stress-strain curves coloured by temperature, and the strain-rate effect at 30 °C");
  const obs = [
    [B("Stress falls with strain in every curve: "), R("on average from 138 to 68 (inferred MPa) over 10 % strain.")],
    [B("Hotter means weaker; "), R("a faster rate starts higher but softens faster, so curves cross near 6 % strain.")],
    [B("Case 60 is irregular "), R("and the only case at 200 °C, 10⁻⁵ /s. We kept it.")],
  ];
  obs.forEach((p, i) => {
    dot(s, 0.6, 4.95 + i * 0.66, String(i + 1), i === 2 ? ORANGE : STEEL, 0.38);
    text(s, p, { x: 1.15, y: 4.97 + i * 0.66, w: 7.1, h: 0.6, fontSize: 14 });
  });
  s.addChart(pres.charts.BAR, [{ name: "Largest stress change (inferred MPa)", labels: ["Temperature", "Strain rate", "Shear modulus G", "Density ρ"], values: [22.12, 17.45, 3.40, 0.19] }], Object.assign({}, AX, {
    x: 8.6, y: 1.7, w: 4.15, h: 4.55, barDir: "bar", barGapWidthPct: 55, chartColors: [HEX.accent1, HEX.dk2, HEX.accent2, HEX.accent4], showLegend: false,
    showTitle: true, title: "Stress change for one level step (inferred MPa)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelFontBold: true,
    valAxisHidden: true, valGridLine: { style: "none" }, catAxisOrientation: "maxMin", valAxisMaxVal: 28, objectName: "factor_chart",
  }));
  text(s, "Mean of the largest gap between paired curves that differ in one input by one level. Stress units inferred as MPa (unconfirmed).", { x: 8.6, y: 6.3, w: 4.15, h: 0.65, fontSize: 11, color: MUTED });
  s.addNotes("Left: all 73 curves. Stress falls with strain in every one, and hotter cases sit lower. Right: at 30 degrees, a faster rate starts higher but softens faster, so the curves cross. The chart compares pairs of cases that differ in one input only: one temperature step moves the curve by 22 units, which we infer to be megapascals, one rate step by 17, shear modulus by 3, and density by only 0.2. So this data says very little about porosity directly; that becomes important for the model.");
}

// ================================================================== 11 Data preparation
{
  const s = content("EDA", 2, "10 · Preparing the data", "From raw histories to a fair train-test split");
  const steps = [
    ["Resample", "Every curve is interpolated to the same 120 strain points (0.02–9.99 %), so slow cases with 100 000 rows don't outweigh fast ones with 1 000."],
    ["Split by case", "Random 50/50 split of whole simulations, as the professor asked: 36 for training, 37 held out from fitting (seed 42)."],
    ["Scale", "Inputs are standardised using training statistics only, so nothing about the test set leaks in."],
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
  s.addNotes("Before modelling, we resample every curve to 120 strain points so that each simulation counts equally. We split whole simulations, not rows, 36 for training and 37 held out from fitting, as the professor asked. Scaling uses training data only. That leaves 4,320 training points, but they come from just 36 independent simulations, which we keep in mind when judging accuracy.");
}

// ================================================================== 12 Choosing the NN
pres.addSection({ title: "Model" });
{
  const s = content("Model", 3, "11 · Choosing the neural network", "Why a physics-informed neural network (JC-PINN)");
  s.addChart(pres.charts.BAR, [
    { name: "Cross-validation on training cases", labels: ["JC equation alone", "Plain MLP", "JC-PINN"], values: [10.24, 2.17, 2.10] },
    { name: "Unseen temperature–rate groups (held out within training)", labels: ["JC equation alone", "Plain MLP", "JC-PINN"], values: [13.95, 11.90, 6.24] },
  ], Object.assign({}, AX, {
    x: 0.6, y: 1.7, w: 7.0, h: 4.15, barDir: "col", barGapWidthPct: 60, chartColors: [HEX.accent4, HEX.accent1], showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    showTitle: true, title: "Mean curve RMSE, training cases only (inferred MPa, lower is better)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelFontSize: 12,
    valAxisMinVal: 0, valAxisMaxVal: 16, valAxisMajorUnit: 4, catAxisLabelFontSize: 13, objectName: "model_choice_chart",
  }));
  const opts = [
    ["Physics only", "The JC equation alone is readable but too rigid: 10.24 error even on training cases.", MUTED],
    ["Data only (plain MLP)", "Fits familiar conditions well (2.17), but errs badly on unseen temperature–rate groups (11.90).", STEEL],
    ["JC-PINN (chosen)", "Chosen for its generalisation on unseen temperature–rate groups (6.24 vs 11.90 for the plain MLP) and its readable constants.", ORANGE],
  ];
  opts.forEach(([h, b, col], i) => {
    const y = 1.7 + i * 1.4;
    card(s, 7.95, y, 4.75, 1.27, i === 2 ? NAVY : ICE);
    text(s, h, { x: 8.15, y: y + 0.12, w: 4.4, h: 0.36, fontSize: 17, bold: true, color: i === 2 ? ORANGE : col === MUTED ? NAVY : col });
    text(s, b, { x: 8.15, y: y + 0.48, w: 4.4, h: 0.78, fontSize: 13.5, color: i === 2 ? WHITE : MUTED });
  });
  text(s, [
    R("Selection used training cases only; the 37 held-out cases were not used. Group-holdout errors were part of the selection score, so they are mildly optimistic. "),
    B("In fairness: ", { color: NAVY }), R("the same network with the JC equation switched off scored slightly better on those groups (5.63) and on test (0.338 vs 0.439), so the accuracy comes from the training recipe (strong weight decay, log-space output), not from the physics. All errors are curve RMSE; stress units inferred as MPa (unconfirmed)."),
  ], { x: 0.6, y: 6.0, w: 12.1, h: 0.95, fontSize: 12, color: MUTED });
  s.addNotes("We compared approaches using only the training cases. The JC equation alone is readable but too rigid, about 10 units of error even on training cases. A plain MLP fits familiar conditions well, 2.17, but when a whole temperature-rate group is hidden its error jumps to 11.9. The JC-PINN multiplies the JC equation by a small learned correction; it scored 6.24 on hidden groups and keeps readable constants, which is why we chose it. Two honest caveats: those group errors were part of the selection score, so they are mildly optimistic; and the same network with the equation switched off did slightly better, 5.63 on groups and 0.338 against 0.439 on test. So the accuracy comes from the training recipe, strong weight decay and a log-space output, not from the physics itself. Units are inferred as megapascals.");
}

// ================================================================== 13 JC-PINN versus a plain MLP
{
  const s = content("Model", 3, "12 · Why JC-PINN", "JC-PINN versus a plain MLP");
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
    row("Plain MLP, 5-16-16-1, 385 weights", "0.143", "11.90", "tried as an alternative; no physics"),
    row("JC-PINN (selected)", "0.439", "6.24", "JC equation × learned correction, 5 seeds", true),
    row("JC-PINN, JC equation switched off (control)", "0.338", "5.63", "post-hoc check, not used for selection"),
    row("JC equation alone", "7.37", "13.95", "too rigid: same curve shape for every condition"),
  ], { x: 0.6, y: 1.75, w: 12.1, colW: [3.6, 2.0, 2.6, 3.9], rowH: [0.6, 0.58, 0.58, 0.58, 0.58], border: { type: "solid", pt: 0.75, color: "D9E6F2" }, margin: [0.04, 0.12, 0.04, 0.12], fontFace: "Calibri", objectName: "why_table" });
  const callouts = [
    ["Familiar conditions", "The plain MLP is more accurate on the random split: 0.143 vs 0.439.", STEEL],
    ["Unseen temperature–rate groups", "JC-PINN halves the plain MLP's error: 6.24 vs 11.90 (mildly optimistic, see below).", ORANGE],
  ];
  callouts.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 6.15;
    card(s, x, 4.95, 5.95, 1.05, ICE);
    s.addShape(pres.shapes.OVAL, { x: x + 0.22, y: 5.14, w: 0.26, h: 0.26, fill: { color: col }, line: { color: col }, objectName: uid("flag") });
    text(s, h, { x: x + 0.62, y: 5.07, w: 5.2, h: 0.34, fontSize: 16, bold: true });
    text(s, b, { x: x + 0.62, y: 5.43, w: 5.2, h: 0.5, fontSize: 13.5, color: MUTED });
  });
  card(s, 0.6, 6.15, 12.1, 0.78, NAVY);
  text(s, [R("Random-split scores measure interpolation between near-duplicate cases; the unseen-group test is closer to real prediction.", { color: WHITE, bold: true }), R("  All errors: curve RMSE, inferred MPa (unconfirmed). Group-holdout errors were part of the selection score.", { color: LINE, fontSize: 12 })],
    { x: 0.85, y: 6.2, w: 11.6, h: 0.68, fontSize: 14, valign: "middle" });
  s.addNotes("All numbers are curve RMSE in stress units we infer to be megapascals. The plain MLP, 5-16-16-1 with 385 weights, scores 0.143 on the random 37-case test but 11.90 on the nine hidden temperature-rate groups. Our JC-PINN, the JC equation times a learned correction trained with 5 seeds, scores 0.439 on the test and 6.24 on hidden groups. A post-hoc control, the same network with the equation switched off, scored 0.338 and 5.63; it was not used for selection, and it shows the accuracy comes from the training recipe. The JC equation alone scores 7.37 and 13.95, because it gives the same curve shape for every condition. The random split mostly tests interpolation between near-duplicate cases, so the group test is the better guide to real prediction, though it is mildly optimistic because it fed the selection score.");
}

// ================================================================== 14 JC-PINN model + training GIF
{
  const s = content("Model", 3, "13 · Data modelling", "JC-PINN: the Johnson–Cook law with a learned correction");
  card(s, 0.6, 1.7, 5.6, 1.25, NAVY);
  text(s, [R("σ  =  σ"), sub("JC"), R("(θ) · exp( δ )")], { x: 0.85, y: 1.82, w: 5.1, h: 0.6, fontSize: 28, bold: true, color: WHITE });
  text(s, [R("σ"), sub("JC"), R(" = [A − Bεⁿ][1 + C ln(ε̇/10⁻⁵)][1 − T*ᵐ][G/G₀]"), sup("q"), R("[1 − φ]"), sup("r")], { x: 0.85, y: 2.42, w: 5.2, h: 0.4, fontSize: 13.5, color: LINE });
  const facts = [
    ["δ network", "5 inputs → 16 → 16 → 1, tanh; 385 weights per network"],
    ["Starts at physics", "δ begins at zero, so the untrained model is exactly the JC law"],
    ["Five seeds", "The same network trained from 5 seeds; predictions combined by geometric mean"],
    ["Training", "Adam 1 500 steps, then L-BFGS 2 500 iterations; strong weight decay; JC constants learned jointly"],
  ];
  facts.forEach(([h, b], i) => {
    const y = 3.2 + i * 0.86;
    dot(s, 0.6, y + 0.04, String(i + 1), i === 1 ? ORANGE : STEEL, 0.38);
    text(s, h, { x: 1.15, y, w: 5.0, h: 0.32, fontSize: 15, bold: true });
    text(s, b, { x: 1.15, y: y + 0.33, w: 5.05, h: 0.5, fontSize: 13, color: MUTED });
  });
  s.addImage({ path: A("gif_training.gif"), x: 6.55, y: 1.85, w: 6.2, h: 6.2 / 2.4, altText: "Animated: JC-PINN curves for four training cases moving onto the simulation data as the training loss falls", objectName: "gif_training" });
  card(s, 6.55, 4.65, 6.2, 1.25, ICE);
  text(s, [B("Watch it learn: "), R("at step 0 the model is the plain JC law (lines off the dots). Adam and then L-BFGS pull the four training curves towards the simulation data as the loss falls about 60-fold.")],
    { x: 6.75, y: 4.75, w: 5.8, h: 1.05, fontSize: 13.5 });
  text(s, "Animated in Slide Show (recorded training run, seed 0). Stress units inferred as MPa (unconfirmed).", { x: 6.55, y: 6.0, w: 6.2, h: 0.3, fontSize: 11, color: MUTED });
  s.addNotes("Our model multiplies the Johnson-Cook law by exp of delta, where delta is a small neural network: five inputs, two hidden layers of 16 tanh units, one output, 385 weights. Delta starts at zero, so before training the model is exactly the physics equation. We train five networks with different seeds and combine them by a geometric mean. The animation is the real recorded training run for seed 0: the lines start as the plain equation and are pulled onto the simulation dots as the loss drops about sixty-fold.");
}

// ================================================================== 15 Evaluation: test GIF
pres.addSection({ title: "Evaluate" });
{
  const s = content("Evaluate", 4, "14 · Evaluation", "Scored on 37 simulations held out from fitting");
  s.addImage({ path: A("gif_test.gif"), x: 0.5, y: 1.7, w: 7.6, h: 7.6 / 2.4, altText: "Animated: JC-PINN prediction against each of the 37 held-out test curves, with the parity plot filling in to R² = 0.9995", objectName: "gif_test" });
  text(s, "Animated in Slide Show: each frame is one held-out case; the right panel collects every point.", { x: 0.6, y: 4.95, w: 7.4, h: 0.3, fontSize: 11, color: MUTED });
  const stats = [["0.44", "mean curve RMSE (inferred MPa)"], ["0.9995", "R² over 4 440 test points"], ["94.9 %", "of points within ±1 (inferred MPa)"], ["37 / 37", "cases better than the JC law alone"]];
  stats.forEach(([v, l], i) => {
    const x = 8.5 + (i % 2) * 2.15, y = 1.8 + Math.floor(i / 2) * 1.55;
    card(s, x, y, 2.0, 1.38, i === 0 ? NAVY : ICE);
    text(s, v, { x: x + 0.15, y: y + 0.18, w: 1.8, h: 0.6, fontSize: 24, bold: true, color: i === 0 ? WHITE : (i === 3 ? ORANGE : NAVY) });
    text(s, l, { x: x + 0.15, y: y + 0.78, w: 1.75, h: 0.55, fontSize: 12.5, color: i === 0 ? LINE : MUTED });
  });
  card(s, 0.6, 5.35, 12.1, 1.5, ICE);
  text(s, [B("How to read it: "), R("37 simulations held out from fitting; scored after the model was locked. "), B("Not a blind test: ", { color: ORANGE }), R("the test cases were explored in earlier project stages. The JC law alone misses by 7.37 on the same cases, so the learned correction cuts the error about 17-fold. Group-holdout errors (slides 12–13) were part of the selection score, so they are mildly optimistic. Stress units inferred as MPa (unconfirmed).")],
    { x: 0.85, y: 5.45, w: 11.6, h: 1.3, fontSize: 14, valign: "middle" });
  s.addNotes("These 37 simulations were held out from fitting and scored after the model was locked. It is not a blind test: the same cases were explored in earlier stages of the project. The animation steps through every held-out case: the orange line is the prediction, the dots are the simulation. Mean curve RMSE is 0.44 in units we infer to be megapascals, R squared is 0.9995 over 4,440 points, and 94.9 percent of points are within plus or minus one unit. It beats the JC law alone, which scores 7.37, on every one of the 37 cases.");
}

// ================================================================== 16 Evaluation: by condition and limits
{
  const s = content("Evaluate", 4, "15 · Evaluation", "Where the model is strongest, and where to be careful");
  s.addChart(pres.charts.BAR, [{ name: "Test RMSE (inferred MPa)", labels: ["30 °C · 10⁻⁵", "30 °C · 10⁻⁴", "30 °C · 10⁻³", "100 °C · 10⁻⁵", "100 °C · 10⁻⁴", "100 °C · 10⁻³", "200 °C · 10⁻⁴", "200 °C · 10⁻³"], values: [0.354, 0.803, 0.182, 0.434, 0.283, 0.454, 0.569, 0.143] }], Object.assign({}, AX, {
    x: 0.6, y: 1.7, w: 6.9, h: 4.4, barDir: "bar", barGapWidthPct: 45, chartColors: [HEX.dk2], showLegend: false,
    showTitle: true, title: "Held-out test error by temperature and strain rate (inferred MPa)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelFontSize: 12,
    catAxisOrientation: "maxMin", catAxisLabelFontSize: 12, valAxisMinVal: 0, valAxisMaxVal: 1.0, valAxisMajorUnit: 0.25, objectName: "condition_chart",
  }));
  const pts = [
    ["Strong", "Every condition stays below 1. The best groups are the fast rates (0.14–0.18).", GREEN],
    ["Weakest", "30 °C at 10⁻⁴ /s (0.80): 8 test cases but only 1 training case at that condition.", ORANGE],
    ["Gaps in the data", "One case at 200 °C · 10⁻⁵ /s and none at 300 °C: predictions there are extrapolation.", STEEL],
    ["Porosity", "Density moves stress by only ≈ 0.2, so the fitted porosity exponent r ≈ 0. Porosity-labelled data is needed.", NAVY],
  ];
  pts.forEach(([h, b, col], i) => {
    const y = 1.7 + i * 1.12;
    s.addShape(pres.shapes.OVAL, { x: 7.95, y: y + 0.08, w: 0.26, h: 0.26, fill: { color: col }, line: { color: col }, objectName: uid("flag") });
    text(s, h, { x: 8.4, y, w: 4.3, h: 0.36, fontSize: 17, bold: true });
    text(s, b, { x: 8.4, y: y + 0.4, w: 4.3, h: 0.68, fontSize: 13.5, color: MUTED });
  });
  text(s, "A plain MLP scored lower on familiar conditions (0.143 vs 0.439 MPa test) but much higher on unseen temperature–rate groups (11.90 vs 6.24). Group-holdout errors were part of the selection score, so they are mildly optimistic. Stress units inferred as MPa (unconfirmed).",
    { x: 0.6, y: 6.25, w: 12.1, h: 0.7, fontSize: 12.5, color: MUTED });
  s.addNotes("Broken down by condition, every held-out group stays under one unit, which we infer to be megapascals. The weakest group, 30 degrees at the middle rate, has eight test cases but only one in training. One case exists at 200 degrees and the slowest rate and none at 300 degrees, so predictions there are extrapolation. Density barely changes the curves, so the fitted porosity exponent is about zero; this data cannot teach the porosity effect on its own. A plain MLP did better on familiar conditions, 0.143 against 0.439, but far worse on unseen groups, 11.90 against 6.24, and those group numbers are mildly optimistic.");
}

// ================================================================== 17 Deployment (planned)
pres.addSection({ title: "Deploy" });
{
  const s = content("Deploy", 5, "16 · Deployment · PLANNED, not yet built", "Planned: a bracket-check tool for aerospace companies");
  const flow = [
    ["Company inputs", "CT-scan porosity and largest pore · service temperature · load rate", NAVY],
    ["JC-PINN service", "Would predict the AlSi10Mg stress–strain curve for those conditions, with range warnings", CYAN],
    ["Ansys material card", "Curve exported as the JC-U hardening table (bridge script exists; integration planned)", STEEL],
    ["Bracket analysis", "Explicit run with the upper-half bore load gives peak σ at the bore", STEEL],
    ["CL check", [R("CL = (1/π)(K"), sub("IC"), R(" ⁄ Yσ)² vs the largest pore, once K"), sub("IC"), R(" and Y are defined")], ORANGE],
  ];
  flow.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 2.48, w = 2.25;
    card(s, x, 1.75, w, 2.4, i === 4 ? NAVY : ICE);
    dot(s, x + 0.2, 1.95, String(i + 1), col, 0.42);
    text(s, h, { x: x + 0.2, y: 2.5, w: w - 0.35, h: 0.6, fontSize: 15.5, bold: true, color: i === 4 ? ORANGE : NAVY });
    text(s, b, { x: x + 0.2, y: 3.05, w: w - 0.3, h: 1.05, fontSize: 12.5, color: i === 4 ? WHITE : MUTED });
    if (i < flow.length - 1) text(s, "›", { x: x + w, y: 2.6, w: 0.23, h: 0.6, fontSize: 30, color: LINE, align: "center" });
  });
  const dec = [["Accept", "largest pore well below CL", GREEN], ["Inspect", "pore close to CL: re-scan or test", ORANGE], ["Reject", "pore at or above CL", "C0392B"]];
  text(s, "PLANNED DECISION FOR EACH PRINTED BRACKET", { x: 0.6, y: 4.45, w: 7, h: 0.26, fontSize: 11, bold: true, color: STEEL, charSpacing: 3 });
  dec.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 2.48;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.85, w: 2.25, h: 1.05, rectRadius: 0.1, fill: { color: col }, line: { color: col }, objectName: uid("decision") });
    text(s, h, { x: x + 0.2, y: 4.93, w: 1.9, h: 0.38, fontSize: 17, bold: true, color: WHITE });
    text(s, b, { x: x + 0.2, y: 5.32, w: 1.95, h: 0.55, fontSize: 12.5, color: WHITE });
  });
  card(s, 8.05, 4.45, 4.65, 2.45, ICE);
  text(s, "HOW IT WOULD BE DELIVERED (PLAN)", { x: 8.3, y: 4.6, w: 4.2, h: 0.26, fontSize: 11, bold: true, color: STEEL, charSpacing: 3 });
  text(s, [
    R("Web app and API around the locked JC-PINN", { bullet: true, breakLine: true }),
    R("Ansys material-card export from our bridge script", { bullet: true, breakLine: true }),
    R("Range checks flag inputs outside the training data", { bullet: true, breakLine: true }),
    R("Retrain as tested, porosity-labelled data arrive", { bullet: true }),
  ], { x: 8.3, y: 4.95, w: 4.25, h: 1.85, fontSize: 13.5, paraSpaceAfter: 4 });
  text(s, [R("The current Model Studio app still serves an earlier MLP; updating it to the JC-PINN is planned. Before release: validate against physical coupon and bracket tests, and define a K"), sub("IC"), R(" source for printed AlSi10Mg.")],
    { x: 0.6, y: 6.1, w: 7.2, h: 0.8, fontSize: 12.5, color: MUTED });
  s.addNotes("This slide is a plan; the tool is not built yet. A company would scan a printed bracket and enter its porosity, largest pore, service temperature and load rate. The JC-PINN would predict the material curve, our existing bridge script would export it as the Ansys JC-U material card, the bracket analysis would give the stress at the bore, and the critical flaw length would be compared with the largest pore once toughness and the shape factor are defined. The tool would then say accept, inspect or reject. Today, the Model Studio app still serves an earlier MLP; moving it to the JC-PINN is planned, and physical validation must come first.");
}

// ================================================================== 18 Limits and open questions
pres.addSection({ title: "Limits" });
{
  const s = content("Limits", 4, "17 · Limits and open questions", "What we have not shown");
  const blocks = [
    ["Evidence", "The test set is not blind. Case 60 (200 °C, 10⁻⁵ /s) is a single irregular case the model cannot fully reproduce. There is no experimental validation.", ORANGE],
    ["Definitions unconfirmed", "Stress units, the meaning of Svm and Evm, why every curve ends below its start, whether density and G represent porosity, and the solver that generated the data.", STEEL],
    ["Porosity", "The fitted exponent r ≈ 0, so these data show almost no porosity effect through the JC formula. Porosity is fixed at 4 % as an assumption, not a model input.", NAVY],
    ["CL not yet computed", [R("Needs the flaw geometry, a K"), sub("IC"), R(" source, the Y factor, the stress at the critical location, and how porosity enters (flow stress, net section, pores as flaws, or toughness). To confirm with the professor.")], CYAN],
  ];
  blocks.forEach(([h, b, col], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.75 + Math.floor(i / 2) * 2.6;
    card(s, x, y, 5.95, 2.4, ICE);
    dot(s, x + 0.25, y + 0.25, String(i + 1), col, 0.48);
    text(s, h, { x: x + 0.9, y: y + 0.3, w: 4.85, h: 0.4, fontSize: 19, bold: true });
    text(s, b, { x: x + 0.9, y: y + 0.82, w: 4.85, h: 1.5, fontSize: 14.5, color: MUTED });
  });
  s.addNotes("Before concluding, what we have not shown. First, evidence: the test set is not blind, case 60 is a single irregular case the model cannot fully reproduce, and nothing is validated against experiments. Second, definitions still to confirm: the stress units, what Svm and Evm mean, why every curve ends below where it starts, whether density and shear modulus stand for porosity, and which solver generated the data. Third, porosity: the fitted exponent is about zero, so the data show almost no porosity effect, and porosity is fixed at 4 percent as an assumption. Fourth, the critical flaw length is not computed yet: it needs the flaw geometry, a toughness source, the shape factor, the stress at the critical location and a rule for how porosity enters. We will confirm these with the professor.");
}

// ================================================================== 19 Conclusion
pres.addSection({ title: "Close" });
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Close" });
  s.addText("CONCLUSION", { placeholder: "kicker" });
  s.addText("What we showed, and what comes next", { placeholder: "title" });
  const pts = [
    ["Realistic bracket model", "Upper-half bore loading and fixed spar faces give a realistic load path; with plasticity the peak stress sits at the bore."],
    ["Plasticity matters", "Elastic analysis overpredicts the peak by 1.85×; our user-defined JC matches Ansys' built-in JC within 0.94 %."],
    ["A material model with readable constants", "JC-PINN predicts 37 held-out simulations to 0.44 mean RMSE (R² = 0.9995) and beats the plain MLP on unseen temperature–rate groups (6.24 vs 11.90, mildly optimistic)."],
    ["Next: CL against porosity · PLANNED, not yet built", [R("Porosity sweep through JC-U, a K"), sub("IC"), R(" source, the flaw geometry and physical tests; then the bracket-check tool.")]],
  ];
  pts.forEach(([h, b], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.8 + Math.floor(i / 2) * 2.4;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.95, h: 2.2, rectRadius: 0.1, fill: { color: "13305A" }, line: { color: i === 3 ? HEX.accent1 : "13305A", width: 1.5 }, objectName: uid("concl") });
    text(s, String(i + 1).padStart(2, "0"), { x: x + 0.3, y: y + 0.2, w: 1.0, h: 0.5, fontSize: 26, bold: true, color: i === 3 ? ORANGE : CYAN });
    text(s, h, { x: x + 0.3, y: y + 0.75, w: 5.4, h: 0.4, fontSize: 18, bold: true, color: i === 3 ? ORANGE : WHITE });
    text(s, b, { x: x + 0.3, y: y + 1.18, w: 5.4, h: 0.95, fontSize: 14, color: PALE });
  });
  text(s, "Ansys results supplied by the team; not independently re-run. Material-data stress units inferred as MPa (unconfirmed).", { x: 0.6, y: 6.62, w: 11, h: 0.3, fontSize: 11, color: LINE });
  s.addNotes("To conclude. Our bracket model loads the bore the way a pin does, and with plasticity the peak sits at the bore. Plasticity matters: an elastic analysis overpredicts the peak by 1.85 times, and our user-defined JC matches Ansys' own within one percent; those Ansys runs are the team's and were not re-run independently. The JC-PINN predicts the 37 held-out simulations to 0.44 mean error and beats the plain MLP on unseen groups, though that comparison is mildly optimistic. Next, and still planned: the porosity sweep, a toughness source, the flaw geometry and physical tests, then the bracket-check tool.");
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
