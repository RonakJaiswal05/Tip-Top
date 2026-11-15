function openStatus() {
  let day = 1, mins = 720;
  try {
    const parts = new Intl.DateTimeFormat("en-GB", { timeZone:"Europe/Berlin", weekday:"short", hour:"2-digit", minute:"2-digit", hourCycle:"h23" }).formatToParts(new Date());
    const g = ty => (parts.find(p => p.type === ty) || {}).value;
    day = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].indexOf(g("weekday")); mins = (+g("hour")) * 60 + (+g("minute"));
  } catch (e) {}
  const openDay = d => d >= 1 && d <= 6;
  if (openDay(day) && mins >= 600 && mins < 1200) return { open:true, text:t("open") };
  let label;
  if (openDay(day) && mins < 600) label = t("today");
  else { let d = (day + 1) % 7, n = 1; while (!openDay(d)) { d = (d + 1) % 7; n++; } label = n === 1 ? t("tomorrow") : t("days")[d]; }
  return { open:false, text:t("closed", { d:label }) };
}
