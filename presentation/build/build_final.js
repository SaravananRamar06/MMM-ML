// Builds "Final Presentation - Porosity in an AM Wing Bracket.pptx" (18 slides).
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
  const terms = [["σ", "stress at the critical location (Ansys)"], ["K", "fracture toughness, falls with porosity"], ["Y", "shape factor of the flaw"]];
  terms.forEach(([sy, d], i) => {
    text(s, sy, { x: 8.0, y: 3.55 + i * 0.55, w: 0.4, h: 0.4, fontSize: 18, bold: true, color: ORANGE });
    text(s, d, { x: 8.45, y: 3.58 + i * 0.55, w: 4.0, h: 0.4, fontSize: 14, color: WHITE });
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
    ["Evaluate", "Scored once on 37 unseen simulations", CYAN],
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
    ["C · User-defined JC", "JC-U", "curve_jcu.png", "our (εp, σ) table", "Multilinear hardening entered point by point from our customised JC law, which includes G and porosity terms.", ORANGE],
  ];
  sims.forEach(([h, code, file, f, b, col], k) => {
    const x = 0.6 + k * 4.12, w = 3.85;
    card(s, x, 2.5, w, 4.3, ICE);
    text(s, [B(code + "  ", { color: col }), R(h, { color: NAVY, bold: true })], { x: x + 0.2, y: 2.62, w: w - 0.4, h: 0.38, fontSize: 16 });
    img(s, file, x + 0.45, 3.05, w - 0.9, 1.3206, `${h} schematic stress-strain curve`);
    text(s, f, { x: x + 0.2, y: 5.2, w: w - 0.4, h: 0.35, fontSize: 13.5, bold: true, color: col === NAVY ? STEEL : col });
    text(s, b, { x: x + 0.2, y: 5.58, w: w - 0.4, h: 1.1, fontSize: 13.5, color: NAVY });
  });
  s.addNotes("We ran three explicit dynamics simulations in Ansys. They share the geometry, mesh set-up and bore load, and differ only in the material card. A is purely elastic. B is elasto-plastic, using Ansys' built-in Johnson-Cook strength model. C is our user-defined Johnson-Cook, where we type in the hardening curve point by point from our own customised Johnson-Cook law, which also carries shear modulus and porosity terms.");
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
    card(s, x, 1.7, w, 5.1, ICE);
    text(s, [B(c + "  ", { color: col }), R(nme, { color: MUTED })], { x: x + 0.2, y: 1.82, w: w - 0.4, h: 0.38, fontSize: 17 });
    img(s, file, x + 0.15, 2.3, w - 0.3, ratio, `${nme}: von Mises stress contour at 0.06 s, maximum ${mx} MPa`);
    text(s, "peak von Mises stress", { x: x + 0.2, y: 5.05, w: w - 0.4, h: 0.28, fontSize: 12.5, color: MUTED });
    text(s, [B(mx, { color: col === NAVY ? STEEL : col }), R(" MPa", { color: NAVY, fontSize: 17 })], { x: x + 0.2, y: 5.33, w: w - 0.4, h: 0.6, fontSize: 32 });
    text(s, where, { x: x + 0.2, y: 5.98, w: w - 0.4, h: 0.6, fontSize: 14 });
  });
  s.addNotes("These are the von Mises stress contours, all at 0.06 seconds. The colour scales differ between pictures, so read the legend numbers. The elastic run peaks at 595 megapascals at the fixed corner of the upper mounting face. Both Johnson-Cook runs peak at about 321 to 324 megapascals around the bore.");
}

// ================================================================== 8 Ansys comparison
{
  const s = content("CAD and Ansys", 1, "07 · Ansys comparison", "Plasticity halves the peak, and our curve matches Ansys");
  s.addChart(pres.charts.BAR, [{ name: "Peak von Mises stress (MPa)", labels: ["EL", "JC-B", "JC-U"], values: [595.27, 320.79, 323.81] }], Object.assign({}, AX, {
    x: 0.6, y: 1.7, w: 5.6, h: 4.9, barDir: "col", barGapWidthPct: 70, chartColors: [HEX.dk2, HEX.dk1, HEX.accent1], showLegend: false,
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
  text(s, "JC-U is the route that lets our own (porosity-aware) material curves drive the bracket model.", { x: 0.6, y: 6.62, w: 12.1, h: 0.35, fontSize: 16, bold: true, color: ORANGE });
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
    ["Density ρ", "2488 · 2619 · 2700 kg/m³  (≈ 7.85 · 3 · 0 % porosity)"],
    ["Shear modulus G", "23 314 · 24 541 · 25 300 MPa"],
    ["Output", "von Mises stress Svm along axial strain E11 = 0–10 %"],
  ];
  vars.forEach(([k, v], i) => {
    const y = 2.4 + i * 0.84;
    text(s, k, { x: 7.6, y, w: 4.9, h: 0.32, fontSize: 15, bold: true, color: i === 4 ? ORANGE : NAVY });
    text(s, v, { x: 7.6, y: y + 0.33, w: 4.9, h: 0.45, fontSize: 13.5, color: MUTED });
  });
  s.addNotes("The professor gave us a design matrix of 108 simulations; 73 have results, about 2.2 million rows of history. Every cell of temperature and strain rate has 9 combinations of density and shear modulus, except 200 degrees at the slowest rate, which has only one case, and 300 degrees, which has none. The porosity values next to density are our inference, assuming fully dense is 2700.");
}

// ================================================================== 10 EDA: curves and factor effects
{
  const s = content("EDA", 2, "09 · Exploratory data analysis", "Temperature and strain rate drive the curves");
  img(s, "eda_curves.png", 0.45, 1.65, 7.9, 2.5581, "All 73 stress-strain curves coloured by temperature, and the strain-rate effect at 30 °C");
  const obs = [
    [B("Stress falls with strain in every curve: "), R("on average from 138 to 68 MPa over 10 % strain.")],
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
  text(s, "Mean of the largest gap between paired curves that differ in one input by one level.", { x: 8.6, y: 6.3, w: 4.15, h: 0.5, fontSize: 11, color: MUTED });
  s.addNotes("Left: all 73 curves. Stress falls with strain in every one, and hotter cases sit lower. Right: at 30 degrees, a faster rate starts higher but softens faster, so the curves cross. The chart compares pairs of cases that differ in one input only: one temperature step moves the curve by 22 megapascals, one rate step by 17, shear modulus by 3, and density by only 0.2. So this data says very little about porosity directly; that becomes important for the model.");
}

// ================================================================== 11 Data preparation
{
  const s = content("EDA", 2, "10 · Preparing the data", "From raw histories to a fair train-test split");
  const steps = [
    ["Resample", "Every curve is interpolated to the same 120 strain points (0.02–9.99 %), so slow cases with 100 000 rows don't outweigh fast ones with 1 000."],
    ["Split by case", "Random 50/50 split of whole simulations, as the professor asked: 36 for training, 37 kept unseen for the final test (seed 42)."],
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
  s.addChart(pres.charts.DOUGHNUT, [{ name: "Split", labels: ["Training cases", "Test cases (unseen)"], values: [36, 37] }], {
    x: 8.2, y: 1.7, w: 4.4, h: 3.9, holeSize: 62, chartColors: [HEX.dk2, HEX.accent1], showLegend: true, legendPos: "b", legendFontSize: 13, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    showValue: true, showPercent: false, dataLabelColor: HEX.lt1, dataLabelFontSize: 16, dataLabelFontBold: true, dataLabelFontFace: "+mn-lt",
    showTitle: true, title: "73 simulations, split by case", titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: HEX.dk1, objectName: "split_chart",
  });
  card(s, 8.2, 5.85, 4.5, 0.95, ICE);
  text(s, "All 120 points of a simulation stay on the same side of the split.", { x: 8.4, y: 5.95, w: 4.1, h: 0.75, fontSize: 14, bold: true, color: STEEL, valign: "middle" });
  s.addNotes("Before modelling, we resample every curve to 120 strain points so that each simulation counts equally. We split whole simulations, not rows, 36 for training and 37 kept aside for one final test, as the professor asked. Scaling uses training data only. That leaves 4,320 training points, but they come from just 36 independent simulations, which we keep in mind when judging accuracy.");
}

// ================================================================== 12 Choosing the NN
pres.addSection({ title: "Model" });
{
  const s = content("Model", 3, "11 · Choosing the neural network", "Why a physics-informed neural network (JC-PINN)");
  s.addChart(pres.charts.BAR, [
    { name: "Cross-validation on training cases", labels: ["JC equation alone", "MLP (1 network)", "MLP (5 networks)", "JC-PINN"], values: [10.24, 2.17, 1.16, 2.10] },
    { name: "Unseen temperature–rate groups", labels: ["JC equation alone", "MLP (1 network)", "MLP (5 networks)", "JC-PINN"], values: [13.95, 11.90, 6.79, 6.24] },
  ], Object.assign({}, AX, {
    x: 0.6, y: 1.7, w: 7.0, h: 4.6, barDir: "col", barGapWidthPct: 60, chartColors: [HEX.accent4, HEX.accent1], showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    showTitle: true, title: "Mean curve error, training side only (MPa, lower is better)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelFontSize: 12,
    valAxisMinVal: 0, valAxisMaxVal: 16, valAxisMajorUnit: 4, catAxisLabelFontSize: 12, objectName: "model_choice_chart",
  }));
  const opts = [
    ["Physics only", "The JC equation is interpretable, but too rigid: 10 MPa error even on training cases.", MUTED],
    ["Data only (MLP)", "Fits seen conditions well, but has no physics and errs more on unseen temperature–rate groups.", STEEL],
    ["JC-PINN (chosen)", "JC equation × a small network correction: lowest error on unseen groups, and physical constants we can read.", ORANGE],
  ];
  opts.forEach(([h, b, col], i) => {
    const y = 1.7 + i * 1.45;
    card(s, 7.95, y, 4.75, 1.3, i === 2 ? NAVY : ICE);
    text(s, h, { x: 8.15, y: y + 0.13, w: 4.4, h: 0.36, fontSize: 17, bold: true, color: i === 2 ? ORANGE : col === MUTED ? NAVY : col });
    text(s, b, { x: 8.15, y: y + 0.5, w: 4.4, h: 0.78, fontSize: 13.5, color: i === 2 ? WHITE : MUTED });
  });
  text(s, "Chosen on training cases only; the 37 test cases were not used. A post-hoc check with the equation switched off scored 1.32 / 5.63 MPa, so the JC backbone is kept for its physical meaning and porosity term rather than for accuracy alone.",
    { x: 0.6, y: 6.38, w: 12.1, h: 0.55, fontSize: 11.5, color: MUTED });
  s.addNotes("We compared three families using only the training cases. The Johnson-Cook equation alone is physical but too rigid. A plain multilayer perceptron fits seen conditions well but has no physics and does worse when a whole temperature-rate group is hidden. The physics-informed network multiplies the Johnson-Cook equation by a small learned correction. It had the lowest error on unseen groups, 6.2 megapascals, and keeps physical constants. In fairness, a later check with the equation switched off was slightly more accurate; we keep the backbone for its physical meaning and its porosity term.");
}

// ================================================================== 13 JC-PINN model + training GIF
{
  const s = content("Model", 3, "12 · Data modelling", "JC-PINN: the Johnson–Cook law with a learned correction");
  card(s, 0.6, 1.7, 5.6, 1.25, NAVY);
  text(s, [R("σ  =  σ"), sub("JC"), R("(θ) · exp( δ )")], { x: 0.85, y: 1.82, w: 5.1, h: 0.6, fontSize: 28, bold: true, color: WHITE });
  text(s, [R("σ"), sub("JC"), R(" = [A − Bεⁿ][1 + C ln(ε̇/10⁻⁵)][1 − T*ᵐ][G/G₀]"), sup("q"), R("[1 − φ]"), sup("r")], { x: 0.85, y: 2.42, w: 5.2, h: 0.4, fontSize: 13.5, color: LINE });
  const facts = [
    ["δ network", "5 inputs → 16 → 16 → 1, tanh; 385 weights each"],
    ["Starts at physics", "δ begins at zero, so the untrained model is exactly the JC law"],
    ["Ensemble", "5 networks with different seeds, averaged"],
    ["Training", "Adam 1 500 steps, then L-BFGS 2 500 iterations; JC constants learned jointly"],
  ];
  facts.forEach(([h, b], i) => {
    const y = 3.2 + i * 0.86;
    dot(s, 0.6, y + 0.04, String(i + 1), i === 1 ? ORANGE : STEEL, 0.38);
    text(s, h, { x: 1.15, y, w: 5.0, h: 0.32, fontSize: 15, bold: true });
    text(s, b, { x: 1.15, y: y + 0.33, w: 5.05, h: 0.45, fontSize: 13, color: MUTED });
  });
  s.addImage({ path: A("gif_training.gif"), x: 6.55, y: 1.85, w: 6.2, h: 6.2 / 2.4, altText: "Animated: JC-PINN curves for four training cases converging onto the simulation data as the training loss falls", objectName: "gif_training" });
  card(s, 6.55, 4.65, 6.2, 1.25, ICE);
  text(s, [B("Watch it learn: "), R("at step 0 the model is the plain JC law (lines off the dots). Adam and then L-BFGS pull the four curves onto the simulation data, including the irregular case 60, as the loss falls 60-fold.")],
    { x: 6.75, y: 4.75, w: 5.8, h: 1.05, fontSize: 13.5 });
  text(s, "Animated in Slide Show (recorded training run, member 0).", { x: 6.55, y: 6.0, w: 6.2, h: 0.3, fontSize: 11, color: MUTED });
  s.addNotes("Our model multiplies the Johnson-Cook law by exp of delta, where delta is a small neural network: five inputs, two hidden layers of 16 tanh units, one output. Delta starts at zero, so before training the model is exactly the physics equation. We train five such networks and average them. The animation is the real training run: the lines start as the plain equation and are pulled onto the simulation dots as the loss drops about sixty-fold.");
}

// ================================================================== 14 Evaluation: test GIF
pres.addSection({ title: "Evaluate" });
{
  const s = content("Evaluate", 4, "13 · Evaluation", "Tested once on 37 simulations it had never seen");
  s.addImage({ path: A("gif_test.gif"), x: 0.5, y: 1.7, w: 7.6, h: 7.6 / 2.4, altText: "Animated: JC-PINN prediction against each of the 37 unseen test curves, with the parity plot filling in to R² = 0.9995", objectName: "gif_test" });
  text(s, "Animated in Slide Show: each frame is one unseen case; the right panel collects every point.", { x: 0.6, y: 4.95, w: 7.4, h: 0.3, fontSize: 11, color: MUTED });
  const stats = [["0.44 MPa", "mean curve error (RMSE)"], ["0.9995", "R² over 4 440 test points"], ["94.9 %", "of points within ±1 MPa"], ["37 / 37", "cases better than the JC law alone"]];
  stats.forEach(([v, l], i) => {
    const x = 8.5 + (i % 2) * 2.15, y = 1.8 + Math.floor(i / 2) * 1.55;
    card(s, x, y, 2.0, 1.38, i === 0 ? NAVY : ICE);
    text(s, v, { x: x + 0.15, y: y + 0.18, w: 1.8, h: 0.6, fontSize: 24, bold: true, color: i === 0 ? WHITE : (i === 3 ? ORANGE : NAVY) });
    text(s, l, { x: x + 0.15, y: y + 0.78, w: 1.75, h: 0.55, fontSize: 12.5, color: i === 0 ? LINE : MUTED });
  });
  card(s, 0.6, 5.45, 12.1, 1.0, ICE);
  text(s, [B("How to read it: "), R("the error is about 0.4 % of a typical stress level. The JC law alone misses by 7.4 MPa on the same cases; the learned correction cuts that by a factor of 17. The model was locked before these cases were scored, and scored once.")],
    { x: 0.85, y: 5.55, w: 11.6, h: 0.8, fontSize: 15, valign: "middle" });
  s.addNotes("This is the real test. The 37 test simulations were never used in training or model choice, and we scored them once. The animation steps through every case: the orange line is the prediction, the dots are the simulation. Mean error is 0.44 megapascals, R squared 0.9995, and 95 percent of points are within one megapascal. It beats the Johnson-Cook law alone on every single case.");
}

// ================================================================== 15 Evaluation: by condition and limits
{
  const s = content("Evaluate", 4, "14 · Evaluation", "Where the model is strongest, and where to be careful");
  s.addChart(pres.charts.BAR, [{ name: "Test RMSE (MPa)", labels: ["30 °C · 10⁻⁵", "30 °C · 10⁻⁴", "30 °C · 10⁻³", "100 °C · 10⁻⁵", "100 °C · 10⁻⁴", "100 °C · 10⁻³", "200 °C · 10⁻⁴", "200 °C · 10⁻³"], values: [0.354, 0.803, 0.182, 0.434, 0.283, 0.454, 0.569, 0.143] }], Object.assign({}, AX, {
    x: 0.6, y: 1.7, w: 6.9, h: 4.7, barDir: "bar", barGapWidthPct: 45, chartColors: [HEX.dk2], showLegend: false,
    showTitle: true, title: "Test error by temperature and strain rate (MPa)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelFontSize: 12,
    catAxisOrientation: "maxMin", catAxisLabelFontSize: 12, valAxisMinVal: 0, valAxisMaxVal: 1.0, valAxisMajorUnit: 0.25, objectName: "condition_chart",
  }));
  const pts = [
    ["Strong", "Every condition stays below 1 MPa. The best groups are the fast rates (0.14–0.18 MPa).", GREEN],
    ["Weakest", "30 °C at 10⁻⁴ /s (0.80 MPa): 8 test cases but only 1 training case at that condition.", ORANGE],
    ["Gaps in the data", "One case at 200 °C · 10⁻⁵ /s and none at 300 °C: predictions there are extrapolation.", STEEL],
    ["Porosity", "Density moves stress by only 0.2 MPa, so the porosity exponent r fits to ≈ 0. Porosity-labelled data is needed.", NAVY],
  ];
  pts.forEach(([h, b, col], i) => {
    const y = 1.7 + i * 1.2;
    s.addShape(pres.shapes.OVAL, { x: 7.95, y: y + 0.08, w: 0.26, h: 0.26, fill: { color: col }, line: { color: col }, objectName: uid("flag") });
    text(s, h, { x: 8.4, y, w: 4.3, h: 0.36, fontSize: 17, bold: true });
    text(s, b, { x: 8.4, y: y + 0.4, w: 4.3, h: 0.75, fontSize: 13.5, color: MUTED });
  });
  text(s, "Plain MLPs scored lower test error (0.06–0.14 MPa) on these familiar conditions, but higher error when whole temperature–rate groups were hidden.", { x: 0.6, y: 6.5, w: 12.1, h: 0.45, fontSize: 12.5, color: MUTED });
  s.addNotes("Broken down by condition, every group stays under one megapascal. The weakest group, 30 degrees at the middle rate, has eight test cases but only one in training. We are honest about the gaps: one case at 200 degrees and the slowest rate, and nothing at 300 degrees, so predictions there are extrapolation. Density barely changes the curves, so this data cannot teach the porosity effect on its own; that needs porosity-labelled data. Plain networks were slightly more accurate on these familiar conditions but worse on unseen groups.");
}

// ================================================================== 16 Deployment
pres.addSection({ title: "Deploy" });
{
  const s = content("Deploy", 5, "15 · Deployment", "A bracket-check tool for aerospace companies");
  const flow = [
    ["Company inputs", "CT-scan porosity and largest pore · service temperature · load rate", NAVY],
    ["JC-PINN service", "Predicts the AlSi10Mg stress–strain curve in milliseconds, with range warnings", CYAN],
    ["Ansys material card", "Curve exported as the JC-U hardening table by our bridge tool", STEEL],
    ["Bracket analysis", "Explicit run with the upper-half bore load gives peak σ at the bore", STEEL],
    ["CL check", [R("CL = (1/π)(K"), sub("IC"), R(" ⁄ Yσ)² compared with the largest pore found")], ORANGE],
  ];
  flow.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 2.48, w = 2.25;
    card(s, x, 1.75, w, 2.4, i === 4 ? NAVY : ICE);
    dot(s, x + 0.2, 1.95, String(i + 1), col, 0.42);
    text(s, h, { x: x + 0.2, y: 2.5, w: w - 0.35, h: 0.6, fontSize: 15.5, bold: true, color: i === 4 ? ORANGE : NAVY });
    text(s, b, { x: x + 0.2, y: 3.1, w: w - 0.3, h: 1.0, fontSize: 12.5, color: i === 4 ? WHITE : MUTED });
    if (i < flow.length - 1) text(s, "›", { x: x + w, y: 2.6, w: 0.23, h: 0.6, fontSize: 30, color: LINE, align: "center" });
  });
  const dec = [["Accept", "largest pore well below CL", GREEN], ["Inspect", "pore close to CL: re-scan or test", ORANGE], ["Reject", "pore at or above CL", "C0392B"]];
  text(s, "DECISION FOR EACH PRINTED BRACKET", { x: 0.6, y: 4.45, w: 6, h: 0.26, fontSize: 11, bold: true, color: STEEL, charSpacing: 3 });
  dec.forEach(([h, b, col], i) => {
    const x = 0.6 + i * 2.48;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.85, w: 2.25, h: 1.05, rectRadius: 0.1, fill: { color: col }, line: { color: col }, objectName: uid("decision") });
    text(s, h, { x: x + 0.2, y: 4.93, w: 1.9, h: 0.38, fontSize: 17, bold: true, color: WHITE });
    text(s, b, { x: x + 0.2, y: 5.32, w: 1.95, h: 0.55, fontSize: 12.5, color: WHITE });
  });
  card(s, 8.05, 4.45, 4.65, 2.4, ICE);
  text(s, "HOW IT IS DELIVERED", { x: 8.3, y: 4.6, w: 4.2, h: 0.26, fontSize: 11, bold: true, color: STEEL, charSpacing: 3 });
  text(s, [
    R("Web app and API around the locked model", { bullet: true, breakLine: true }),
    R("One-click Ansys material export", { bullet: true, breakLine: true }),
    R("Range checks flag inputs outside the training data", { bullet: true, breakLine: true }),
    R("Retrain as companies add tested, porosity-labelled data", { bullet: true }),
  ], { x: 8.3, y: 4.95, w: 4.25, h: 1.85, fontSize: 13.5, paraSpaceAfter: 4 });
  text(s, [R("Before release: validate against physical coupon and bracket tests, and fix a K"), sub("IC"), R(" source for printed AlSi10Mg.")], { x: 0.6, y: 6.15, w: 7.2, h: 0.6, fontSize: 12.5, color: MUTED });
  s.addNotes("Deployment is the last stage of the life cycle. A company scans a printed bracket and enters its porosity, largest pore, service temperature and load rate. Our model predicts the material curve in milliseconds, exports it as the Ansys material card, the bracket analysis gives the stress at the bore, and the critical flaw length is compared with the largest pore. The tool then says accept, inspect, or reject. It is delivered as a web app and API with range checks, and retrained as companies add tested data. Before real use it must be validated against physical tests.");
}

// ================================================================== 17 Conclusion
pres.addSection({ title: "Close" });
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Close" });
  s.addText("CONCLUSION", { placeholder: "kicker" });
  s.addText("What we showed, and what comes next", { placeholder: "title" });
  const pts = [
    ["Realistic bracket model", "Upper-half bore loading and fixed spar faces give the true load path; the peak stress sits at the bore."],
    ["Plasticity matters", "Elastic analysis overpredicts the peak by 1.85×. Our user-defined JC matches Ansys' built-in JC within 0.94 %."],
    ["An accurate, physical material model", "JC-PINN predicts 37 unseen simulations to 0.44 MPa (R² = 0.9995), and is best on unseen temperature–rate groups."],
    ["Next: CL against porosity", [R("Porosity sweep through JC-U, a K"), sub("IC"), R(" source and physical tests, then release the bracket-check tool.")]],
  ];
  pts.forEach(([h, b], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.85 + Math.floor(i / 2) * 2.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.95, h: 2.35, rectRadius: 0.1, fill: { color: "13305A" }, line: { color: i === 3 ? HEX.accent1 : "13305A", width: 1.5 }, objectName: uid("concl") });
    text(s, String(i + 1).padStart(2, "0"), { x: x + 0.3, y: y + 0.25, w: 1.0, h: 0.55, fontSize: 26, bold: true, color: i === 3 ? ORANGE : CYAN });
    text(s, h, { x: x + 0.3, y: y + 0.85, w: 5.4, h: 0.4, fontSize: 19, bold: true, color: WHITE });
    text(s, b, { x: x + 0.3, y: y + 1.3, w: 5.4, h: 0.95, fontSize: 15, color: PALE });
  });
  s.addNotes("To conclude. Our bracket model loads the bore the way a pin really does, and the peak sits at the bore. Plasticity matters: an elastic analysis nearly doubles the peak, and our user-defined Johnson-Cook matches Ansys' own. Our physics-informed network predicts unseen simulations to 0.44 megapascals. Next we sweep porosity through JC-U, add a toughness source and physical tests, and release the bracket-check tool.");
}

// ================================================================== 18 Thank you
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
