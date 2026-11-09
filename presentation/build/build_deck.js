// Builds "Porosity in an AM Wing Rib Bracket.pptx".
// Run: NODE_PATH=<dir containing pptxgenjs> node build_deck.js <dir containing scripts/apply_theme.js>
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(path.join(process.argv[2], "scripts/apply_theme.js"));

const A = (f) => path.join(__dirname, "..", "assets", f);
const OUT = path.join(__dirname, "..", "Porosity in an AM Wing Rib Bracket.pptx");

const THEME = {
  name: "Wing Bracket",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "14213D", lt1: "FFFFFF", dk2: "2F5D8A", lt2: "EEF2F6",
    accent1: "E8590C", accent2: "2F5D8A", accent3: "6B7785", accent4: "9AA6B2",
    accent5: "DCE4EC", accent6: "1F8A70", hlink: "2F5D8A", folHlink: "6B7785",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.title = "Effect of Porosity on an AM Wing Rib Bracket";
pres.author = "Pranav Parasuram C, R Saravanan, Dinesh Y, Amit Narayan K";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const INK = C.text1, STEEL = C.text2, ORANGE = C.accent1, MUTED = C.accent3, LINE = C.accent4,
  TINT = C.background2, PALE = C.accent5, WHITE = C.background1;
const FOOT = "Porosity in an AM wing rib bracket  ·  Multiscale Modelling of Materials using ML";

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: INK },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.15, w: 11.5, h: 2.75, fontSize: 44, bold: true, color: WHITE, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.05, w: 11.5, h: 0.6, fontSize: 22, italic: true, color: LINE, align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: WHITE },
  margin: [0.5, 0.6, 0.7, 0.6],
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.42, w: 12.1, h: 0.32, fontSize: 12, bold: true, color: ORANGE, charSpacing: 3, align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.74, w: 12.1, h: 0.8, fontSize: 34, bold: true, color: INK, valign: "top", align: "left", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: 0.6, y: 7.02, w: 9, h: 0.3, fontSize: 10, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: 12.23, y: 7.02, w: 0.5, h: 0.3, fontSize: 10, color: MUTED, align: "right", margin: 0 },
});
pres.defineSlideMaster({
  title: "CLOSING_DARK",
  background: { color: INK },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.42, w: 12.1, h: 0.32, fontSize: 12, bold: true, color: ORANGE, charSpacing: 3, align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.74, w: 12.1, h: 0.8, fontSize: 34, bold: true, color: WHITE, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.23, y: 7.02, w: 0.5, h: 0.3, fontSize: 10, color: LINE, align: "right", margin: 0 },
});

// ------------------------------------------------------------------ helpers
let n = 0;
const uid = (s) => `${s}_${++n}`;
function content(section, kicker, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(kicker.toUpperCase(), { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  return s;
}
function text(s, t, o) {
  s.addText(t, Object.assign({ isTextBox: true, margin: 0, fontSize: 16, color: INK, valign: "top", objectName: uid("txt") }, o));
}
function card(s, x, y, w, h, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill || TINT }, line: { color: fill || TINT }, objectName: uid("card") });
}
function num(s, x, y, label, color) {
  s.addShape(pres.shapes.OVAL, { x, y, w: 0.46, h: 0.46, fill: { color: color || INK }, line: { color: color || INK }, objectName: uid("dot") });
  s.addText(label, { x, y, w: 0.46, h: 0.46, isTextBox: true, margin: 0, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle", objectName: uid("dotlbl") });
}
function img(s, file, x, y, w, ratio, alt) {
  s.addImage({ path: A(file), x, y, w, h: w / ratio, altText: alt, objectName: uid("img") });
}
const B = (t, o) => ({ text: t, options: Object.assign({ bold: true }, o) });
const R = (t, o) => ({ text: t, options: Object.assign({}, o) });

// ================================================================== 1 Title
pres.addSection({ title: "Introduction" });
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Introduction" });
  s.addText("Effect of Porosity on an\nAdditively Manufactured\nWing Rib Bracket", { placeholder: "title" });
  s.addText("AlSi10Mg  ·  explicit dynamics with elastic and Johnson–Cook material models", { placeholder: "body" });
  s.addShape(pres.shapes.LINE, { x: 0.8, y: 4.95, w: 0.9, h: 0, line: { color: ORANGE, width: 2.5 }, objectName: "title_rule" });
  text(s, "Pranav Parasuram C  ·  R Saravanan  ·  Dinesh Y  ·  Amit Narayan K", { x: 0.8, y: 5.25, w: 11.5, h: 0.4, fontSize: 18, color: WHITE });
  text(s, "Multiscale Modelling of Materials using Machine Learning  ·  IIITDM Kancheepuram", { x: 0.8, y: 5.7, w: 11.5, h: 0.35, fontSize: 14, color: LINE });
  s.addNotes("Introduce the team and the one-line topic: how the pores left by 3D printing reduce the size of defect our aluminium wing rib bracket can survive.");
}

// ================================================================== 2 Problem statement
{
  const s = content("Introduction", "Problem statement", "Printing the bracket leaves pores inside it");
  text(s, [
    R("Our wing rib bracket is made by "), B("laser powder-bed fusion"), R(" (metal 3D printing) in "), B("AlSi10Mg"), R(" aluminium alloy."),
  ], { x: 0.6, y: 1.85, w: 6.6, h: 0.8, fontSize: 20 });
  text(s, [
    R("Melting powder layer by layer traps "), B("gas pores"), R(" and leaves "), B("lack-of-fusion voids"), R(". Some porosity is unavoidable."),
  ], { x: 0.6, y: 2.85, w: 6.6, h: 0.8, fontSize: 20 });
  text(s, [
    R("Every pore is a ready-made flaw. ", { color: MUTED }), B("Under load, a pore can become the crack that breaks the part.", { color: INK }),
  ], { x: 0.6, y: 3.85, w: 6.6, h: 0.8, fontSize: 20 });
  card(s, 0.6, 5.05, 6.6, 1.45, PALE);
  text(s, "OUR QUESTION", { x: 0.9, y: 5.25, w: 6, h: 0.3, fontSize: 12, bold: true, color: STEEL, charSpacing: 3 });
  text(s, "How large a flaw can the porous bracket tolerate before it fractures?", { x: 0.9, y: 5.6, w: 6.1, h: 0.8, fontSize: 20, bold: true, italic: true });
  // porous section illustration
  card(s, 7.9, 1.85, 4.8, 4.65, TINT);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.3, y: 2.3, w: 4.0, h: 3.0, rectRadius: 0.08, fill: { color: LINE }, line: { color: INK, width: 1.25 }, objectName: "section" });
  const pores = [[8.7, 2.7, 0.22], [9.6, 3.3, 0.14], [10.4, 2.6, 0.3], [11.4, 3.0, 0.18], [9.0, 4.3, 0.26], [10.1, 4.0, 0.12], [11.0, 4.6, 0.22], [11.8, 4.1, 0.14], [9.9, 4.85, 0.16], [8.65, 3.55, 0.12], [11.65, 2.55, 0.1]];
  pores.forEach(([x, y, d], i) => s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d * (i % 3 === 0 ? 0.7 : 1), fill: { color: WHITE }, line: { color: INK, width: 0.75 }, objectName: uid("pore") }));
  s.addShape(pres.shapes.OVAL, { x: 10.4, y: 2.6, w: 0.3, h: 0.3, fill: { color: WHITE }, line: { color: ORANGE, width: 2 }, objectName: "pore_hl" });
  text(s, "Printed cross-section (schematic)", { x: 8.3, y: 5.45, w: 4.0, h: 0.3, fontSize: 12, color: MUTED, align: "center" });
  text(s, "Porosity φ = pore volume ÷ total volume", { x: 8.3, y: 5.8, w: 4.0, h: 0.3, fontSize: 14, bold: true, color: INK, align: "center" });
  s.addNotes("The bracket is printed, not machined from solid. Printing always leaves some pores. Each pore is a flaw already inside the part, so the real question is how big a flaw the bracket can carry before it fractures.");
}

// ================================================================== 3 Objective
{
  const s = content("Introduction", "Objective", "Predict the critical flaw length as porosity rises");
  text(s, [R("Critical flaw length "), B("C"), B("L", { subscript: true }), R(" is the largest pore or crack the bracket can carry at its working stress before it fractures.")],
    { x: 0.6, y: 1.8, w: 12.1, h: 0.5, fontSize: 18, color: MUTED });
  card(s, 0.6, 2.55, 6.0, 2.6, INK);
  text(s, "Linear-elastic fracture mechanics", { x: 0.95, y: 2.8, w: 5.4, h: 0.35, fontSize: 14, color: LINE });
  text(s, [R("C"), R("L", { subscript: true }), R("  =  "), R("1", {}), R(" ⁄ π  ·  ( K"), R("IC", { subscript: true }), R(" ⁄ Y σ )²")],
    { x: 0.95, y: 3.35, w: 5.4, h: 0.9, fontSize: 36, bold: true, color: WHITE });
  text(s, "Target: the curve CL(φ), with φ = 4 % as our study point (assumed).", { x: 0.95, y: 4.4, w: 5.4, h: 0.6, fontSize: 15, color: WHITE });
  const terms = [
    ["σ", "Stress at the critical location", "From the Ansys bracket model, driven by our material model.", STEEL],
    ["K", [R("Fracture toughness K"), R("IC", { subscript: true }), R("(φ)")], "Falls as porosity rises; taken from literature for AlSi10Mg.", ORANGE],
    ["Y", "Flaw shape factor", "Depends on pore shape and position (e.g. surface vs. embedded).", MUTED],
  ];
  terms.forEach(([sym, head, body, col], i) => {
    const y = 2.55 + i * 0.9;
    num(s, 7.05, y + 0.1, sym, col);
    text(s, head, { x: 7.7, y: y + 0.02, w: 5.0, h: 0.35, fontSize: 18, bold: true });
    text(s, body, { x: 7.7, y: y + 0.38, w: 5.0, h: 0.45, fontSize: 14, color: MUTED });
  });
  text(s, [R("Smaller C"), R("L", { subscript: true }), R(" means less tolerance: the same pore that is harmless in dense metal can be critical in porous metal.")],
    { x: 0.6, y: 5.6, w: 12.1, h: 0.6, fontSize: 18, bold: true, color: INK });
  s.addNotes("CL stands for critical flaw length, not lift. The formula needs three things: the stress at the critical spot, which comes from our Ansys model; the fracture toughness, which drops with porosity; and a shape factor for the flaw. Our goal is to plot CL against porosity, using 4 percent as our study point.");
}

// ================================================================== 4 Real-time impact
pres.addSection({ title: "In service" });
{
  const s = content("In service", "Impact during real-time conditions", "How porosity affects the bracket in flight");
  text(s, "WHAT THE BRACKET SEES", { x: 0.6, y: 1.8, w: 4.2, h: 0.3, fontSize: 12, bold: true, color: STEEL, charSpacing: 3 });
  const env = [
    ["Cyclic flight loads", "Gusts and manoeuvres load and unload the bracket thousands of times."],
    ["Shock and vibration", "Take-off, landing and engine vibration add sudden peaks."],
    ["Temperature swings", "Cold at cruise altitude, hot on the ground: strength and toughness shift."],
  ];
  env.forEach(([h, b], i) => {
    const y = 2.2 + i * 1.45;
    card(s, 0.6, y, 4.2, 1.25, TINT);
    text(s, h, { x: 0.85, y: y + 0.15, w: 3.8, h: 0.35, fontSize: 17, bold: true });
    text(s, b, { x: 0.85, y: y + 0.52, w: 3.8, h: 0.65, fontSize: 14, color: MUTED });
  });
  text(s, "WHAT A PORE DOES TO IT", { x: 5.3, y: 1.8, w: 7.4, h: 0.3, fontSize: 12, bold: true, color: STEEL, charSpacing: 3 });
  const chain = [
    ["Pore", "Removes material, so the remaining metal carries more stress."],
    ["Stress concentration", "Local stress around a round pore is about 2× the average."],
    ["Crack starts", "Repeated flight loads start a fatigue crack at the pore."],
    ["Crack grows", "The crack lengthens a little with every load cycle."],
    ["Fracture", "Sudden failure once the crack reaches CL."],
  ];
  chain.forEach(([h, b], i) => {
    const y = 2.2 + i * 0.86;
    const last = i === chain.length - 1;
    num(s, 5.3, y + 0.05, String(i + 1), last ? ORANGE : INK);
    if (!last) s.addShape(pres.shapes.LINE, { x: 5.53, y: y + 0.53, w: 0, h: 0.37, line: { color: LINE, width: 1.5 }, objectName: uid("link") });
    text(s, h, { x: 5.95, y: y + 0.07, w: 2.6, h: 0.4, fontSize: 17, bold: true, color: last ? ORANGE : INK });
    text(s, b, { x: 8.45, y: y + 0.08, w: 4.3, h: 0.6, fontSize: 14, color: MUTED });
  });
  card(s, 5.3, 6.4, 7.4, 0.5, PALE);
  text(s, "Stiffness barely changes, so a deflection check will not reveal the danger.", { x: 5.5, y: 6.47, w: 7.1, h: 0.36, fontSize: 15, bold: true, color: STEEL });
  s.addNotes("In flight the bracket is loaded and unloaded continuously, with shocks at take-off and landing and big temperature swings. A pore concentrates stress, roughly doubling it locally for a round pore. Repeated loading starts a crack there, the crack grows each cycle, and the part fails when the crack reaches the critical flaw length. Porosity hardly changes stiffness, so a simple deflection test would not warn us.");
}

// ================================================================== 5 CAD model
pres.addSection({ title: "CAD and loads" });
{
  const s = content("CAD and loads", "CAD model", "Wing rib bracket: Rib Bracket.STEP");
  img(s, "cad_planform.png", 0.7, 1.7, 5.15, 1.026, "Planform of the rib bracket with overall dimensions, the bore, the two arms and the two mounting faces labelled");
  const stats = [["231.5 × 230", "planform envelope, mm"], ["40 mm", "plate thickness"], ["778 cm³", "volume (≈ 2.1 kg fully dense)"], ["Ø10 mm", "bore: where the load enters"]];
  stats.forEach(([v, l], i) => {
    const x = 6.55 + (i % 2) * 3.15, y = 1.85 + Math.floor(i / 2) * 1.35;
    text(s, v, { x, y, w: 3.0, h: 0.65, fontSize: 34, bold: true, color: i === 3 ? ORANGE : INK });
    text(s, l, { x, y: y + 0.66, w: 3.0, h: 0.35, fontSize: 14, color: MUTED });
  });
  const pts = [
    [B("Two arms meet at the bore: "), R("a lower arm and a diagonal arm form an open triangle, which keeps the part stiff and light.")],
    [B("Two 50 × 40 mm mounting faces "), R("bolt the bracket to the wing spar at x = 210 mm.")],
    [B("Same geometry in all three runs: "), R("EL, JC-B and JC-U all import this one STEP file.")],
  ];
  pts.forEach((p, i) => text(s, p, { x: 6.55, y: 4.65 + i * 0.68, w: 6.2, h: 0.62, fontSize: 15 }));
  s.addNotes("This is the bracket from our STEP file. The lower arm and the diagonal arm meet at the 10 mm bore, where the load comes in, and two mounting faces on the right bolt it to the spar. The same geometry is used in all three simulations, so any difference in results comes from the material model.");
}

// ================================================================== 6 Forces
{
  const s = content("CAD and loads", "Loads and supports", "Forces acting on the bracket");
  img(s, "forces.png", 0.55, 1.7, 7.55, 1.549, "Free-body diagram: upward bearing force F on the upper half of the bore, fixed supports at the two mounting faces, reactions R and moment M = F × 210 mm");
  const items = [
    ["F", "Applied load", "Bearing force from the pin, acting along +Y on the upper half of the Ø10 bore.", ORANGE],
    ["▥", "Fixed support", "Both spar mounting faces are fixed in all directions.", INK],
    ["R", "Reactions", "The spar pushes back with R = F and a moment M = F × 210 mm.", STEEL],
    ["⇄", "Load path", "The lower arm is stretched and the diagonal arm is squeezed, carrying the load to the spar.", MUTED],
  ];
  items.forEach(([sym, h, b, col], i) => {
    const y = 1.85 + i * 1.22;
    num(s, 8.45, y, sym, col);
    text(s, h, { x: 9.1, y: y - 0.02, w: 3.65, h: 0.38, fontSize: 18, bold: true, color: col === MUTED ? INK : col });
    text(s, b, { x: 9.1, y: y + 0.38, w: 3.65, h: 0.75, fontSize: 14, color: MUTED });
  });
  s.addNotes("The load comes in through a pin in the bore. It pushes upward, along plus Y, on the upper half of the bore. Both mounting faces are fixed. For equilibrium the spar pushes back with a force equal to F and a moment of F times the 210 mm lever arm. Inside the bracket the lower arm is in tension and the diagonal arm is in compression.");
}

// ================================================================== 7 Why upper half
{
  const s = content("CAD and loads", "Load application", "Why we load only the upper half of the bore");
  img(s, "bore_detail.png", 0.6, 1.75, 6.9, 1.793, "Two bore close-ups: a load on the whole bore pulls the lower half into the hole; a pin load presses only on the upper half, leaving a gap below");
  const why = [
    [B("A pin can only push. "), R("It presses on the side the load drives it into, the upper half here; the lower half opens a gap and carries nothing.")],
    [B("Loading the whole bore is wrong twice. "), R("It pulls the lower half into the hole, which no pin can do, and spreads F over twice the area, underestimating stress at the bore.")],
    [B("The CAD already splits the bore "), R("into two half-faces of 628 mm² each, so we apply F to the upper face exactly.")],
    [B("It is standard practice: "), R("a bearing load is applied only on the compressive side of a bolt or pin hole.")],
  ];
  why.forEach((p, i) => {
    const y = 1.85 + i * 1.18;
    num(s, 7.85, y, String(i + 1).padStart(2, "0"), i === 0 ? ORANGE : INK);
    text(s, p, { x: 8.5, y: y - 0.03, w: 4.25, h: 1.08, fontSize: 15 });
  });
  card(s, 0.6, 5.85, 6.9, 0.85, PALE);
  text(s, "Result: the peak stress sits where it really occurs, at the top of the bore, which is where a pore matters most.", { x: 0.85, y: 5.95, w: 6.45, h: 0.68, fontSize: 15, bold: true, color: STEEL, valign: "middle" });
  s.addNotes("A pin can only push, so only the half of the hole it presses against carries load. If we put the force on the whole bore, Ansys would pull the lower half into the hole, which is physically impossible, and the force would be spread over double the area, so the stress at the bore would come out too low. The CAD already splits the bore into upper and lower faces, so we can load the upper one exactly. This is also how bearing loads are normally modelled.");
}

// ================================================================== 8 Comparison study set-up
pres.addSection({ title: "Comparison study" });
{
  const s = content("Comparison study", "Comparison Study - Final.wbpj", "Three explicit simulations, one variable");
  text(s, [R("Same bracket, same "), B("Explicit Dynamics (AUTODYN)"), R(" solver. Only the "), B("material law", { color: ORANGE }), R(" changes, so every difference in the results comes from the material model.")],
    { x: 0.6, y: 1.75, w: 12.1, h: 0.75, fontSize: 18 });
  const sys = [
    ["A", "EL", "Elastic", "AlSi10Mg - EL"],
    ["B", "JC-B", "Built-in JC", "AlSi10Mg - JCB"],
    ["C", "JC-U", "User Defined JC", "AlSi10Mg - JCU"],
  ];
  const cells = ["Engineering Data", "Geometry", "Model", "Setup", "Solution", "Results"];
  sys.forEach(([letter, code, name, mat], k) => {
    const x = 0.6 + k * 4.2, w = 3.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.75, w, h: 3.95, rectRadius: 0.1, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: { type: "outer", color: "14213D", opacity: 0.12, blur: 6, offset: 2, angle: 90 }, objectName: uid("sys") });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.75, w, h: 0.75, rectRadius: 0.1, fill: { color: k === 0 ? STEEL : k === 1 ? INK : ORANGE }, line: { color: k === 0 ? STEEL : k === 1 ? INK : ORANGE }, objectName: uid("syshead") });
    text(s, [B(code + "   "), R(name, { bold: false })], { x: x + 0.25, y: 2.86, w: w - 0.5, h: 0.52, fontSize: 18, color: WHITE, valign: "middle" });
    cells.forEach((c, j) => {
      const y = 3.68 + j * 0.47;
      text(s, `${j + 1}`, { x: x + 0.25, y, w: 0.3, h: 0.36, fontSize: 13, color: MUTED, valign: "middle" });
      text(s, c, { x: x + 0.6, y, w: 1.6, h: 0.36, fontSize: 14, color: INK, valign: "middle", bold: j === 0 });
      const detail = j === 0 ? mat : j === 1 ? "Rib Bracket.STEP" : j === 3 ? "upper-half bore load" : "";
      if (detail) text(s, detail, { x: x + 1.95, y, w: w - 2.15, h: 0.36, fontSize: 12.5, color: j === 0 ? ORANGE : MUTED, valign: "middle", align: "right" });
    });
  });
  s.addNotes("Our Workbench project has three Explicit Dynamics systems: Elastic, Built-in Johnson-Cook and User Defined Johnson-Cook. Each one uses the same Rib Bracket STEP file and the same solver. The only thing we change is the material card, so we can see exactly what the material model does to the bracket's response.");
}

// ================================================================== 9 EL
{
  const s = content("Comparison study", "Simulation 1 · EL", "Elastic: the linear baseline");
  card(s, 0.6, 1.8, 5.6, 4.85, TINT);
  img(s, "curve_el.png", 0.85, 2.05, 5.1, 1.321, "Schematic stress-strain line for the elastic model, which keeps rising past the real alloy's yield point");
  text(s, "Stress is proportional to strain at every load level.", { x: 0.85, y: 6.0, w: 5.1, h: 0.45, fontSize: 14, color: MUTED });
  text(s, "MATERIAL CARD  ·  AlSi10Mg - EL", { x: 6.7, y: 1.85, w: 6, h: 0.3, fontSize: 12, bold: true, color: STEEL, charSpacing: 3 });
  const props = [["ρ", "Density"], ["E", "Young's modulus"], ["ν", "Poisson's ratio"]];
  props.forEach(([sym, l], i) => {
    const x = 6.7 + i * 2.05;
    text(s, sym, { x, y: 2.25, w: 1.9, h: 0.7, fontSize: 36, bold: true, color: INK });
    text(s, l, { x, y: 2.95, w: 1.9, h: 0.35, fontSize: 14, color: MUTED });
  });
  const rows = [
    ["Shows", "Where stress concentrates and how stiff the bracket is."],
    ["Misses", "Yielding and plastic strain. Beyond yield the stress it reports is too high."],
    ["Role", "Reference line: the JC runs show what plasticity adds to it."],
  ];
  rows.forEach(([h, b], i) => {
    const y = 3.75 + i * 0.95;
    text(s, h, { x: 6.7, y, w: 1.3, h: 0.4, fontSize: 18, bold: true, color: i === 1 ? ORANGE : INK });
    text(s, b, { x: 8.0, y: y + 0.02, w: 4.75, h: 0.8, fontSize: 16 });
  });
  s.addNotes("The Elastic run uses only density, Young's modulus and Poisson's ratio. Stress stays proportional to strain however hard we load it, so it shows where stress concentrates but can never yield. Past the yield point its stress is too high and it shows no plastic strain. We use it as the baseline.");
}

// ================================================================== 10 JC-B
{
  const s = content("Comparison study", "Simulation 2 · JC-B", "Built-in Johnson–Cook strength model");
  card(s, 0.6, 1.8, 12.1, 1.3, INK);
  text(s, [R("σ"), R("y", { subscript: true }), R("  =  ( A + B ε"), R("p", { subscript: true }), R("ⁿ )  ·  ( 1 + C ln ε̇* )  ·  ( 1 − T*ᵐ )")],
    { x: 0.9, y: 1.98, w: 11.5, h: 0.95, fontSize: 34, bold: true, color: WHITE, valign: "middle" });
  const terms = [
    ["Strain hardening", [R("A + B ε"), R("p", { subscript: true }), R("ⁿ")], "A initial yield, B hardening constant, n hardening exponent"],
    ["Strain rate", "1 + C ln ε̇*", "C rate constant, with ε̇* = ε̇ / ε̇₀ (reference strain rate)"],
    ["Thermal softening", "1 − T*ᵐ", "m softening exponent, T* scaled between room and melting temperature"],
  ];
  terms.forEach(([h, f, b], i) => {
    const y = 3.35 + i * 1.12;
    num(s, 0.6, y + 0.05, String(i + 1), i === 0 ? ORANGE : INK);
    text(s, h, { x: 1.25, y, w: 2.6, h: 0.38, fontSize: 17, bold: true });
    text(s, f, { x: 3.85, y, w: 2.2, h: 0.38, fontSize: 17, bold: true, color: STEEL });
    text(s, b, { x: 1.25, y: y + 0.42, w: 5.2, h: 0.6, fontSize: 14, color: MUTED });
  });
  img(s, "curve_jcb.png", 7.0, 3.3, 3.95, 1.321, "Schematic Johnson-Cook stress-strain curves: yield then hardening, higher for faster loading and lower when hotter");
  text(s, "Ansys' own Johnson–Cook card, plus thermal data (specific heat, conductivity, expansion, melting point) for the temperature term.", { x: 7.0, y: 6.38, w: 5.7, h: 0.55, fontSize: 13, color: MUTED });
  s.addNotes("JC-B uses the Johnson-Cook strength model that is built into Ansys. The yield stress is a product of three terms: strain hardening, a strain-rate term and a thermal-softening term. The card stores A, B, n, C, m, the melting temperature and a reference strain rate, plus the thermal properties the temperature term needs. It captures yielding, hardening, rate and temperature, but its constants are generic and say nothing about porosity.");
}

// ================================================================== 11 JC-U
{
  const s = content("Comparison study", "Simulation 3 · JC-U", "User-defined JC: our curve, entered point by point");
  img(s, "curve_jcu.png", 0.6, 1.8, 5.1, 1.321, "Schematic multilinear hardening curve built from user-supplied stress and plastic strain points");
  text(s, "Multilinear isotropic hardening: Ansys joins our points with straight lines.", { x: 0.6, y: 5.75, w: 5.1, h: 0.6, fontSize: 14, color: MUTED });
  text(s, "MATERIAL CARD  ·  AlSi10Mg - JCU", { x: 6.3, y: 1.85, w: 6.4, h: 0.3, fontSize: 12, bold: true, color: STEEL, charSpacing: 3 });
  text(s, [R("Instead of Ansys' fixed constants, we give a table of "), B("(plastic strain, stress)"), R(" pairs computed from our own customised Johnson–Cook law:")],
    { x: 6.3, y: 2.25, w: 6.4, h: 0.85, fontSize: 16 });
  card(s, 6.3, 3.2, 6.4, 1.05, TINT);
  text(s, [R("σ = [A − B εⁿ] [1 + C ln ε̇*] [1 − T*ᵐ] [G/G₀]"), R("q", { superscript: true }), R(" [1 − φ]"), R("r", { superscript: true })], { x: 6.5, y: 3.3, w: 6.0, h: 0.85, fontSize: 19, bold: true, color: INK, valign: "middle" });
  const rows = [
    [B("Adds two terms: "), R("shear modulus G and "), B("porosity φ", { color: ORANGE }), R(", which the built-in model cannot see.")],
    [B("Any curve fits in: "), R("including our trained JC-PINN prediction at a chosen porosity.")],
    [B("Trade-off: "), R("one table describes one condition. A new rate or temperature needs a new table.")],
  ];
  rows.forEach((p, i) => text(s, p, { x: 6.3, y: 4.5 + i * 0.72, w: 6.4, h: 0.66, fontSize: 15 }));
  s.addNotes("JC-U uses multilinear isotropic hardening: we type in stress against plastic strain and Ansys joins the points. The points come from our customised Johnson-Cook equation, which adds a shear-modulus term and a porosity term. That is the door through which porosity, and our machine-learning material model, enter the bracket simulation. The catch is that one table covers one temperature and strain rate.");
}

// ================================================================== 12 Comparison
pres.addSection({ title: "Comparison" });
{
  const s = content("Comparison", "EL vs JC-B vs JC-U", "What each material model can capture");
  const Y = "✓", N = "—";
  const hdr = (t, fill) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: fill }, align: "center", valign: "middle", fontSize: 16 } });
  const cell = (t, o) => ({ text: t, options: Object.assign({ align: "center", valign: "middle", fontSize: 15, color: INK }, o) });
  const lab = (t) => ({ text: t, options: { bold: true, align: "left", valign: "middle", fontSize: 15, color: INK } });
  const ok = (t) => cell(t || Y, { color: STEEL, bold: true, fontSize: t ? 14 : 18 });
  const no = (t) => cell(t || N, { color: LINE, fontSize: t ? 14 : 18 });
  const rows = [
    [{ text: "", options: { fill: { color: WHITE } } }, hdr("EL", STEEL), hdr("JC-B", INK), hdr("JC-U", ORANGE)],
    [lab("Elastic stiffness"), ok(), ok(), ok()],
    [lab("Yield and plastic strain"), no(), ok(), ok()],
    [lab("Strain hardening"), no(), ok("power law"), ok("any measured curve")],
    [lab("Strain-rate effect"), no(), ok(), no("fixed by the table")],
    [lab("Temperature effect"), no(), ok(), no("fixed by the table")],
    [lab("Porosity effect"), no(), no(), ok("through our curve")],
    [lab("Inputs needed"), cell("ρ, E, ν", { fontSize: 14 }), cell("+ 7 JC constants", { fontSize: 14 }), cell("+ stress–strain table", { fontSize: 14 })],
  ];
  s.addTable(rows, {
    x: 0.6, y: 1.8, w: 7.9, colW: [2.65, 1.5, 1.75, 2.0], rowH: 0.56,
    border: { type: "solid", pt: 0.75, color: "DCE4EC" }, fill: { color: WHITE }, fontFace: "Calibri", objectName: "compare_table",
  });
  text(s, "EXPECTED IN THE RESULTS", { x: 9.0, y: 1.85, w: 3.75, h: 0.3, fontSize: 12, bold: true, color: STEEL, charSpacing: 3 });
  const exp = [
    ["EL", "Highest peak: it cannot yield, so its stress keeps rising with load.", STEEL],
    ["JC-B", "Lower peak: yielding and hardening cap the stress.", INK],
    ["JC-U", "Close to JC-B if our curve is right; any gap comes only from the curve.", ORANGE],
  ];
  exp.forEach(([c, b, col], i) => {
    const y = 2.3 + i * 1.33;
    card(s, 9.0, y, 3.75, 1.18, TINT);
    text(s, c, { x: 9.2, y: y + 0.12, w: 3.4, h: 0.35, fontSize: 17, bold: true, color: col });
    text(s, b, { x: 9.2, y: y + 0.48, w: 3.4, h: 0.65, fontSize: 14, color: INK });
  });
  text(s, "Only JC-U can carry porosity into the bracket model, so it is our route to CL(φ).", { x: 0.6, y: 6.45, w: 12.1, h: 0.4, fontSize: 18, bold: true, color: ORANGE });
  s.addNotes("Elastic captures stiffness only. Built-in Johnson-Cook adds yield, hardening, strain-rate and temperature effects, but with generic constants. User-defined Johnson-Cook loses the automatic rate and temperature dependence, because each table is for one condition, but it is the only one that can include porosity, through our own curve. We expect EL to give the highest peak because it cannot yield, JC-B to give a lower, capped peak, and JC-U to land close to JC-B if our curve is right.");
}

// ================================================================== 13 Results
{
  const s = content("Comparison", "Results · equivalent stress at t = 0.06 s", "Where the bracket is most stressed");
  const sims = [
    ["EL", "Elastic", STEEL, "result_el.png", 1.370, "595.27", "at the fixed corner of the upper mounting face"],
    ["JC-B", "Built-in JC", INK, "result_jcb.png", 1.370, "320.79", "around the bore, where the load enters"],
    ["JC-U", "User Defined JC", ORANGE, "result_jcu.png", 1.388, "323.81", "around the bore, where the load enters"],
  ];
  sims.forEach(([c, nme, col, file, ratio, mx, where], k) => {
    const x = 0.6 + k * 4.12, w = 3.85;
    card(s, x, 1.75, w, 4.95, TINT);
    text(s, [B(c + "  ", { color: col }), R(nme, { color: MUTED })], { x: x + 0.2, y: 1.88, w: w - 0.4, h: 0.4, fontSize: 18 });
    img(s, file, x + 0.15, 2.38, w - 0.3, ratio, `${nme} run: equivalent (von Mises) stress contour on the bracket at 0.06 s, maximum ${mx} MPa`);
    text(s, "max von Mises stress", { x: x + 0.2, y: 5.1, w: w - 0.4, h: 0.3, fontSize: 13, color: MUTED });
    text(s, [B(mx, { color: col }), R(" MPa", { color: INK, bold: false, fontSize: 18 })], { x: x + 0.2, y: 5.38, w: w - 0.4, h: 0.6, fontSize: 32 });
    text(s, where, { x: x + 0.2, y: 6.02, w: w - 0.4, h: 0.55, fontSize: 14, color: INK });
  });
  s.addNotes("These are the three Workbench contours of von Mises stress, all read at the same time, 0.06 seconds. The colour scales are different in each picture, so compare the legend numbers rather than the colours. Elastic peaks at 595 megapascals at the fixed corner of the upper mounting face. Both Johnson-Cook runs peak at about 321 to 324 megapascals around the bore.");
}

// ================================================================== 14 Results comparison
{
  const s = content("Comparison", "EL vs JC-B vs JC-U · results", "Plasticity halves the peak; our curve matches Ansys");
  s.addChart(pres.charts.BAR, [{ name: "Max von Mises stress (MPa)", labels: ["EL", "JC-B", "JC-U"], values: [595.27, 320.79, 323.81] }], {
    x: 0.6, y: 1.75, w: 5.6, h: 4.7, barDir: "col", barGapWidthPct: 70,
    chartColors: ["2F5D8A", "14213D", "E8590C"], showLegend: false,
    showTitle: true, title: "Max von Mises stress at t = 0.06 s (MPa)", titleFontSize: 14, titleColor: "14213D", titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 16, dataLabelFontBold: true, dataLabelColor: "14213D", dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "0.0",
    catAxisLabelColor: "14213D", catAxisLabelFontSize: 16, catAxisLabelFontFace: "+mn-lt", catAxisLabelFontBold: true,
    valAxisLabelColor: "6B7785", valAxisLabelFontSize: 12, valAxisLabelFontFace: "+mn-lt", valAxisMinVal: 0, valAxisMaxVal: 700, valAxisMajorUnit: 100,
    valGridLine: { color: "DCE4EC", size: 0.75 }, catGridLine: { style: "none" }, objectName: "max_stress_chart",
  });
  const finds = [
    ["1.85×", "EL overpredicts", "Without yielding, stress keeps rising: 595 MPa against about 322 MPa for both JC runs.", STEEL],
    ["0.94 %", "JC-U agrees with JC-B", "323.81 vs 320.79 MPa: our user-defined curve gives the same answer as Ansys' built-in model.", ORANGE],
    ["Bore", "The peak moves to the bore", "EL peaks at the fixed mounting-face corner; with plasticity the peak sits where the pin load enters.", INK],
  ];
  finds.forEach(([big, h, b, col], i) => {
    const y = 1.75 + i * 1.5;
    card(s, 6.6, y, 6.1, 1.32, TINT);
    text(s, big, { x: 6.8, y: y + 0.2, w: 1.75, h: 0.9, fontSize: 30, bold: true, color: col, valign: "middle" });
    text(s, h, { x: 8.6, y: y + 0.14, w: 3.95, h: 0.38, fontSize: 17, bold: true });
    text(s, b, { x: 8.6, y: y + 0.52, w: 3.95, h: 0.75, fontSize: 14, color: MUTED });
  });
  text(s, "JC-U matches Ansys' own JC and peaks at the bore, so it is the model we use to add porosity.", { x: 0.6, y: 6.5, w: 12.1, h: 0.4, fontSize: 18, bold: true, color: ORANGE });
  s.addNotes("The elastic model gives a peak 1.85 times higher, because it never yields. The two Johnson-Cook runs agree within one percent, 320.8 against 323.8 megapascals, which tells us our user-defined curve behaves like Ansys' own Johnson-Cook model. With plasticity the peak moves from the fixed corner of the mounting face to the bore, where the pin load enters. That is the stress location we need for the critical flaw length, and it is why JC-U is the model we take forward with porosity.");
}

// ================================================================== 14 Approach
pres.addSection({ title: "Approach" });
{
  const s = pres.addSlide({ masterName: "CLOSING_DARK", sectionTitle: "Approach" });
  s.addText("HOW WE REACH THE OBJECTIVE", { placeholder: "kicker" });
  s.addText("From material model to critical flaw length", { placeholder: "title" });
  const steps = [
    ["Material model", "JC-PINN trained on the 73 professor-supplied AlSi10Mg simulations: 0.44 MPa mean curve error on 37 held-out cases, R² = 0.9995.", "DONE"],
    ["Material into Ansys", "Export the predicted curve as the JC-U hardening table, using our material bridge tool.", "READY"],
    ["Bracket stress", "JC-U with the upper-half bore load: peak 323.8 MPa, located at the bore.", "DONE"],
    ["Porosity sweep", "Repeat for φ = 0, 4 % (study point) and above, giving σ(φ) and K", "NOW", "IC", "(φ)."],
    ["Critical flaw length", "CL = (1/π)(K", "NEXT", "IC", " ⁄ Yσ)² for each φ, giving the CL(φ) curve."],
  ];
  steps.forEach(([h, b0, tag, sub, rest], i) => {
    const b = sub ? [R(b0), R(sub, { subscript: true }), R(rest)] : b0;
    const x = 0.6 + i * 2.48, w = 2.25;
    const done = tag === "DONE" || tag === "READY";
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.95, w, h: 3.55, rectRadius: 0.1, fill: { color: "1D2E52" }, line: { color: tag === "NOW" ? "E8590C" : "1D2E52", width: 1.5 }, objectName: uid("step") });
    text(s, String(i + 1).padStart(2, "0"), { x: x + 0.22, y: 2.15, w: 1.0, h: 0.6, fontSize: 30, bold: true, color: tag === "NOW" ? ORANGE : LINE });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + w - 0.98, y: 2.27, w: 0.78, h: 0.32, rectRadius: 0.08, fill: { color: done ? "1F8A70" : tag === "NOW" ? "E8590C" : "3A4A6B" }, line: { color: done ? "1F8A70" : tag === "NOW" ? "E8590C" : "3A4A6B" }, objectName: uid("chip") });
    text(s, tag, { x: x + w - 0.98, y: 2.27, w: 0.78, h: 0.32, fontSize: 10, bold: true, color: WHITE, align: "center", valign: "middle", charSpacing: 1 });
    text(s, h, { x: x + 0.22, y: 2.95, w: w - 0.4, h: 0.7, fontSize: 18, bold: true, color: WHITE });
    text(s, b, { x: x + 0.22, y: 3.7, w: w - 0.4, h: 2.0, fontSize: 14, color: "C9D3DD" });
    if (i < steps.length - 1) text(s, "›", { x: x + w, y: 3.55, w: 0.23, h: 0.6, fontSize: 28, color: LINE, align: "center" });
  });
  text(s, "STILL TO PIN DOWN", { x: 0.6, y: 5.9, w: 3, h: 0.3, fontSize: 12, bold: true, color: ORANGE, charSpacing: 3 });
  text(s, [R("A literature K"), R("IC", { subscript: true }), R(" for printed AlSi10Mg  ·  the flaw shape factor Y  ·  confirmation of how density and G map to porosity")], { x: 0.6, y: 6.25, w: 12.1, h: 0.4, fontSize: 15, color: WHITE });
  s.addNotes("Step one is done: our physics-informed JC-PINN reproduces the professor's simulations to about 0.44 MPa on cases it never saw. Its curve goes into Ansys as the JC-U table. The bracket run with the upper-half bore load is done: JC-U peaks at 323.8 megapascals at the bore. Now we repeat that across porosity levels and feed stress and toughness into the fracture formula to get critical flaw length against porosity. We still need a literature toughness value, a flaw shape factor and confirmation of the porosity mapping.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
